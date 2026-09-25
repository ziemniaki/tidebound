# Tidebound: original project code. Internal codename; no final game title chosen.
# Pure Ruby domain model. No maps, rendering, or Essentials globals required.
module Tidebound
  VERSION = "0.8.3"

  module Config
    # Prototype tuning values, not settled design decisions.
    REST_HP_FRACTION = 0.25
    RECOVERY_HP_FRACTION = 0.25
    SPIRIT_CATCH_RATE = 35
    SPIRIT_TURN_LIMIT = 6
    BLOCKED_ITEMS = [:ANTIDOTE, :FULLHEAL, :FULLRESTORE, :PECHABERRY,
                     :LUMBERRY, :LAVACOOKIE, :OLDGATEAU, :CASTELIACONE,
                     :LUMIOSEGALETTE, :SHALOURSABLE, :BIGMALASADA,
                     :HEALPOWDER, :PEWTERCRUNCHIES].freeze
  end

  class TransitionError < StandardError; end

  def self.copy(value)
    Marshal.load(Marshal.dump(value))
  end

  def self.identity(pokemon)
    pokemon.instance_variable_get(:@tidebound_identity)
  end

  def self.borrowed?(pokemon)
    !!pokemon.instance_variable_get(:@tidebound_borrowed)
  end

  def self.restore_floor(pokemon, fraction)
    floor = [(pokemon.totalhp * fraction).ceil, 1].max
    pokemon.hp = [pokemon.hp, floor].max
    # No status healing; resting repeatedly cannot accumulate HP above the floor.
    pokemon
  end

  class Soul
    attr_reader :id, :pokemon, :location, :journey
    attr_accessor :status, :reason

    def initialize(id, pokemon, location, journey)
      @id = id
      @pokemon = Tidebound.copy(pokemon)
      @location = Tidebound.copy(location)
      @journey = journey
      @status = :waiting
      @reason = nil
    end
  end

  class State
    attr_reader :schema_version, :realm, :journey, :souls, :memorials, :story
    attr_accessor :checkpoint

    def initialize
      @schema_version = 1
      @realm = :living
      @journey = 0
      @next_identity = 1
      @souls = []
      @memorials = []
      @checkpoint = nil
      @story = {
        :suicune => :unmet,
        :mystic_sabre => false,
        :final_demon_defeated => false,
        :koga_imitation_defeated => false
      }
    end

    def assign_identity(pokemon)
      existing = Tidebound.identity(pokemon)
      return existing if existing
      id = "companion-#{@next_identity}"
      @next_identity += 1
      pokemon.instance_variable_set(:@tidebound_identity, id)
      id
    end

    def enter_astral!(party, location)
      raise TransitionError, "Already in the astral plane" unless @realm == :living
      members = party.reject { |p| Tidebound.borrowed?(p) }
      raise TransitionError, "No companions to recover" if members.empty?
      raise TransitionError, "Maximum party size is six" if members.length > 6
      raise TransitionError, "Eggs are outside this prototype" if members.any?(&:egg?)
      ids = members.map { |p| assign_identity(p) }
      raise TransitionError, "Duplicate companion identity" unless ids.uniq.length == ids.length
      lost_ids = @memorials.map(&:id)
      raise TransitionError, "A permanently lost companion cannot return" unless (ids & lost_ids).empty?
      next_journey = @journey + 1
      records = members.map do |p|
        Soul.new(Tidebound.identity(p), p, location, next_journey)
      end
      @souls = records
      @journey = next_journey
      @realm = :astral
      records.map(&:id)
    end

    def soul(id)
      @souls.find { |s| s.id == id } || (raise TransitionError, "Unknown spirit: #{id}")
    end

    def waiting_ids
      @souls.select { |s| s.status == :waiting }.map(&:id)
    end

    def begin_encounter!(id)
      ensure_astral!
      raise TransitionError, "Another spirit encounter is active" if @souls.any? { |s| s.status == :engaged }
      record = soul(id)
      raise TransitionError, "This spirit's opportunity is already spent" unless record.status == :waiting
      # Prepare the copy before spending the encounter opportunity.
      opponent = Tidebound.copy(record.pokemon)
      opponent.heal
      opponent.item = nil
      record.status = :engaged
      opponent
    end

    def recover!(id)
      ensure_astral!
      record = soul(id)
      raise TransitionError, "Spirit is not in an encounter" unless record.status == :engaged
      # Return the original snapshot, not the engine's newly owned caught copy.
      companion = Tidebound.copy(record.pokemon)
      Tidebound.restore_floor(companion, Config::RECOVERY_HP_FRACTION)
      record.status = :recovered
      companion
    end

    def lose!(id, reason = :escaped)
      ensure_astral!
      record = soul(id)
      unless [:waiting, :engaged].include?(record.status)
        raise TransitionError, "Spirit is already resolved"
      end
      record.status = :lost
      record.reason = reason
      @memorials << Tidebound.copy(record)
      nil
    end

    def leave_astral!
      ensure_astral!
      raise TransitionError, "Finish the active encounter first" if @souls.any? { |s| s.status == :engaged }
      waiting_ids.each { |id| lose!(id, :left_behind) }
      @realm = :living
      true
    end

    def rest!(party)
      raise TransitionError, "Resting fires belong to the living world" unless @realm == :living
      party.each do |p|
        next if p.egg? || Tidebound.borrowed?(p)
        Tidebound.restore_floor(p, Config::REST_HP_FRACTION)
        # A small PP floor avoids a no-moves softlock. No cumulative refill.
        p.moves.each { |move| move.pp = 1 if move.pp == 0 && move.total_pp > 0 }
      end
    end

    def cemetery_team(fallback, size = 6)
      raise ArgumentError, "Team size must be 1..6" unless (1..6).include?(size)
      fallen = @memorials.last(size).map { |s| Tidebound.copy(s.pokemon) }
      missing = size - fallen.length
      raise ArgumentError, "Not enough fallback Pokemon" if fallback.length < missing
      team = fallen + fallback.first(missing).map { |p| Tidebound.copy(p) }
      team.each(&:heal)
      team
    end

    def resolve_suicune!(choice)
      allowed = {
        :unmet => [:corrupted],
        :corrupted => [:rescued, :killed],
        :rescued => [:healed, :lost],
        :healed => [:lost],
        :killed => [], :lost => []
      }
      unless allowed.fetch(@story[:suicune]).include?(choice)
        raise TransitionError, "Invalid Suicune story transition"
      end
      @story[:suicune] = choice
    end

    def ending
      return :unfinished unless @story[:final_demon_defeated]
      return :restoration if @story[:suicune] == :healed && @story[:mystic_sabre]
      :dark_victory
    end

    private

    def ensure_astral!
      raise TransitionError, "Not in the astral plane" unless @realm == :astral
    end
  end
end

