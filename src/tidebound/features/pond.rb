# The southern pond: fishing battles, water terrain and optional items.
GameData::EncounterType.register(id: :PondGrass, type: :land, trigger_chance: 18)
module Tidebound::Pond
  module_function
  def flags
    Tidebound.story[:pond] ||= {}
  end
  def psyduck
    return if flags[:shoreduck_gone]
    return unless pbConfirmMessage("A Psyduck watches the shallows, holding its head. Approach?")
    return unless Tidebound::Encounters.able?
    outcome = Tidebound::Encounters.fight(:PSYDUCK, 8)
    flags[:shoreduck_gone] = true if [1, 4].include?(outcome)
  end
  def here?
    $game_map && $game_map.map_id == 108
  end
  def water?(x, y)
    $game_map.terrain_tag(x, y).id == :StillWater
  end
  def say(*lines)
    lines.each { |line| pbMessage(line) }
  end
  FISHERS = {
    toma: {
      name: "Toma",
      team: [[:MAGIKARP, 9], [:GOLDEEN, 10]],
      invite:
        "Toma: The sea takes my hooks. This pond usually gives them back. Care for a little battle while the fish ignore us?",
      loss: "Toma: Well played. Even a quiet pond has its surprises.",
      after: "Toma: That duck comes here when the road gets noisy. We leave the shallow bank to it."
    },
    ida: {
      name: "Ida",
      team: [[:WOOPER, 10], [:POLIWAG, 11]],
      invite:
        "Ida: I mend nets for the dock crews. This is where I rest my hands. Shall we let our companions stretch instead?",
      loss: "Ida: A useful lesson. Thank you for taking the time.",
      after:
        "Ida: I can see marks on that stone, but I can't read them from here. And I'm certainly not swimming across."
    },
    renzo: {
      name: "Renzo",
      team: [[:BARBOACH, 12]],
      invite:
        "Renzo: Aipom stole my bait. Then it came back for the lid. Help me recover a little dignity with a battle?",
      loss: "Renzo: There goes the dignity. At least I still have the bucket.",
      after:
        "Renzo: Someone used to prune the berry tree. I take two and leave the rest. Seems only fair."
    }
  }.freeze
  def fisher(id)
    fisher = FISHERS.fetch(id)
    return say(fisher.fetch(:after)) if flags[id]
    return unless pbConfirmMessage(fisher.fetch(:invite))
    return unless Tidebound::Encounters.able?
    result =
      Tidebound::Encounters.trainer(
        type: :FISHERMAN,
        name: fisher.fetch(:name),
        loss: fisher.fetch(:loss),
        team: fisher.fetch(:team),
        departure: nil
      )
    if result == 1
      flags[id] = true
      say(fisher.fetch(:loss), fisher.fetch(:after))
    end
  end
  def hidden_item
    return say("Only dry leaves remain in the little hollow.") if flags[:cache]
    say("Behind the roots, something has been wrapped in old waxed cloth.")
    flags[:cache] = true if pbReceiveItem(:MYSTICWATER)
  end
end
module Tidebound::PondEncounters
  def encounter_type
    type = super
    return :PondGrass if type == :Land && Tidebound::Pond.here? && $game_player.y >= 48
    type
  end
end
PokemonEncounters.prepend(Tidebound::PondEncounters)
Tidebound::Actors.on_frame("shore_duck") do |_event, _actor|
  !Tidebound::Pond.flags[:shoreduck_gone]
end
