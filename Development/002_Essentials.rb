# Integration targets the inspected Pokemon Essentials v21.1 interfaces.
# Only battles explicitly launched with this API use the prototype death loop.
# Do not treat this plugin as a finished global death/healing replacement.
module Tidebound
  class << self
    attr_accessor :battle_context, :before_cleanup_party, :spirit_capture
  end

  def self.state
    $tidebound ||= State.new
  end

  def self.location
    {:map_id => $game_map.map_id, :x => $game_player.x, :y => $game_player.y}
  end

  def self.checkpoint!(map_id, x, y, direction = 2)
    state.rest!($player.party)
    state.checkpoint = [map_id, x, y, direction]
  end

  # The map event must perform Transfer Player after an :astral return value.
  def self.wild!(*foes)
    living_battle! { WildBattle.start_core(*foes) }
  end

  def self.trainer!(*trainers)
    living_battle! { TrainerBattle.start_core(*trainers) }
  end

  # Both kinds of living-world battle retain the pre-heal loss snapshot.
  def self.living_battle!
    raise TransitionError, "Living-world battle requested in astral plane" unless state.realm == :living
    raise TransitionError, "Party needs an able Pokemon" if $player.able_pokemon_count == 0
    raise TransitionError, "Set a resting-fire checkpoint first" unless state.checkpoint
    $player.party.each { |p| state.assign_identity(p) }
    origin = location
    self.battle_context = :living
    self.before_cleanup_party = nil
    setBattleRule("canLose", "noPartner", "noMoney")
    outcome = yield
    if [2, 5].include?(outcome)
      raise TransitionError, "Missing pre-heal battle snapshot" unless before_cleanup_party
      state.enter_astral!(before_cleanup_party, origin)
      $player.party.clear
      return :astral
    end
    outcome
  ensure
    self.battle_context = nil
    self.before_cleanup_party = nil
  end

  # Explicitly provisional: a borrowed guide enables the first spirit battle.
  # It cannot become a permanent companion or a cemetery entry.
  def self.borrow_guide!
    raise TransitionError, "Guide only exists in astral plane" unless state.realm == :astral
    existing = $player.party.find { |p| borrowed?(p) }
    return existing if existing
    raise TransitionError, "Party is full" if $player.party.length >= 6
    level = state.souls.map { |s| s.pokemon.level }.max || 5
    guide = Pokemon.new(:NATU, level)
    guide.name = "Guide"
    guide.instance_variable_set(:@tidebound_borrowed, true)
    guide.heal
    $player.party << guide
    guide
  end

  def self.recover_spirit!(id)
    raise TransitionError, "An able guide or companion is required" if $player.able_pokemon_count == 0
    original_party = copy($player.party)
    opponent = state.begin_encounter!(id)
    self.battle_context = :spirit
    self.before_cleanup_party = nil
    self.spirit_capture = nil
    setBattleRule("canLose", "noPartner", "noMoney", "noExp", "single")
    outcome = WildBattle.start_core(opponent)
    # Remove Essentials' defeat auto-heal, if it happened. Only the guide resets.
    if [2, 5].include?(outcome) && before_cleanup_party
      $player.party.replace(before_cleanup_party)
    end
    if outcome == 4
      unless spirit_capture && identity(spirit_capture) == id
        raise TransitionError, "Engine capture did not match the expected spirit"
      end
      restored = state.recover!(id)
      # A guide + five recovered Pokemon may occupy all six positions.
      $player.party.reject! { |p| borrowed?(p) } if $player.party.length >= 6
      $player.party << restored
      return :recovered
    end
    state.lose!(id, [2, 5].include?(outcome) ? :battle_lost : :encounter_failed)
    :lost
  rescue StandardError
    # Technical faults must not consume a player's one narrative opportunity.
    record = state.souls.find { |s| s.id == id }
    if state.realm == :astral && record && record.status == :engaged
      record.status = :waiting
      $player.party.replace(original_party) if original_party
    end
    raise
  ensure
    $player.party.each { |p| p.heal if borrowed?(p) } if $player
    self.battle_context = nil
    self.before_cleanup_party = nil
    self.spirit_capture = nil
  end

  def self.return_to_living!
    raise TransitionError, "Not in the astral plane" unless state.realm == :astral
    survivors = $player.party.reject { |p| borrowed?(p) }
    # Provisional fallback: an ordinary Natu, explicitly not a recovered friend.
    if survivors.empty?
      fallback = Pokemon.new(:NATU, 5)
      state.assign_identity(fallback)
      fallback.hp = 1
      restore_floor(fallback, Config::RECOVERY_HP_FRACTION)
      survivors << fallback
    end
    state.leave_astral!
    $player.party.replace(survivors)
    state.rest!($player.party)
    state.checkpoint
  end
end

# Essentials 21.1 validates Symbol constants without nested path lookup.
TideboundSaveState = Tidebound::State unless defined?(TideboundSaveState)

if defined?(SaveData)
  SaveData.register(:tidebound) do
    ensure_class :TideboundSaveState
    save_value { Tidebound.state }
    load_value { |value| $tidebound = value }
    new_game_value { Tidebound::State.new }
    reset_on_new_game
  end
end

if defined?(BattleCreationHelperMethods)
  module Tidebound::CaptureBeforeCleanup
    def after_battle(outcome, can_lose)
      if Tidebound.battle_context
        Tidebound.before_cleanup_party = Tidebound.copy($player.party)
      end
      super
    end
  end
  BattleCreationHelperMethods.singleton_class.prepend(Tidebound::CaptureBeforeCleanup)
end

# Intercept storage only during our spirit encounter. The original saved object
# is restored by recover_spirit!, so owner, nickname, IVs, moves and item survive.
if defined?(Battle)
  module Tidebound::SpiritBattle
    def pbCaptureCalc(pokemon, battler, catch_rate, ball)
      rate = Tidebound.battle_context == :spirit ? Tidebound::Config::SPIRIT_CATCH_RATE : catch_rate
      super(pokemon, battler, rate, ball)
    end

    def pbEndOfRoundPhase
      super
      return unless Tidebound.battle_context == :spirit && @decision == 0
      @tidebound_spirit_rounds = (@tidebound_spirit_rounds || 0) + 1
      if @tidebound_spirit_rounds >= Tidebound::Config::SPIRIT_TURN_LIMIT
        pbDisplay(_INTL("The familiar shape dissolves into the mist."))
        @decision = 3
      end
    end

    def pbStorePokemon(pokemon)
      if Tidebound.battle_context == :spirit
        Tidebound.spirit_capture = pokemon
        return
      end
      super
    end
  end
  Battle.prepend(Tidebound::SpiritBattle)
end
