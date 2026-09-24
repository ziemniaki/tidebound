# Small test doubles exercise our code without RGSS, graphics, or game assets.
# These tests do not claim to replace a playtest in the actual Essentials runtime.
module TestSuite
  @passed = 0
  @failed = 0

  def self.test(name)
    yield
    @passed += 1
    puts "PASS #{name}"
  rescue StandardError => e
    @failed += 1
    puts "FAIL #{name}: #{e.class}: #{e.message}"
    puts e.backtrace.first(3)
  end

  def self.assert(condition, message = "Assertion failed")
    raise message unless condition
  end

  def self.equal(expected, actual)
    assert(expected == actual, "Expected #{expected.inspect}, got #{actual.inspect}")
  end

  def self.raises(type)
    begin
      yield
    rescue type
      return
    end
    raise "Expected #{type}"
  end

  def self.finish
    puts "#{@passed} passed; #{@failed} failed"
    raise "Test suite failed" if @failed > 0
  end
end

class TestMove
  attr_accessor :id, :pp, :total_pp
  def initialize(id, pp = 7)
    @id, @pp, @total_pp = id, pp, 15
  end
end

class Pokemon
  attr_accessor :species, :level, :name, :hp, :totalhp, :status, :moves,
                :item, :owner, :iv, :ev, :personalID, :form, :egg
  def initialize(species, level = 5)
    @species, @level, @name = species, level, "Moss"
    @totalhp, @hp, @status = 40, 40, :NONE
    @moves = [TestMove.new(:PECK), TestMove.new(:LEER, 0)]
    @item, @owner, @personalID = :MYSTICSABRE, {:name => "Keeper", :id => 18}, 12345
    @iv, @ev, @form, @egg = {:HP => 29}, {:HP => 8}, 1, false
  end
  def egg?; @egg; end
  def heal
    @hp, @status = @totalhp, :NONE
    @moves.each { |m| m.pp = m.total_pp }
  end
end

class TestPlayer
  attr_accessor :party
  def initialize(party); @party = party; end
  def able_pokemon_count; @party.count { |p| !p.egg? && p.hp > 0 }; end
end

module SaveData
  @registry = {}
  class Value
    attr_reader :save_proc, :load_proc, :new_proc, :reset
    def ensure_class(klass); @klass = klass; end
    def save_value(&block); @save_proc = block; end
    def load_value(&block); @load_proc = block; end
    def new_game_value(&block); @new_proc = block; end
    def reset_on_new_game; @reset = true; end
  end
  def self.register(key, &block)
    value = Value.new
    value.instance_eval(&block)
    @registry[key] = value
  end
  def self.value(key); @registry.fetch(key); end
end

module BattleCreationHelperMethods
  # Models v21.1's documented canLose defeat cleanup, the integration hazard
  # our adapter must intercept before original companion records are healed.
  def self.after_battle(outcome, can_lose)
    $player.party.each(&:heal) if [2, 5].include?(outcome) && can_lose
  end
end

class Battle
  attr_accessor :decision, :received_rate, :messages, :stored
  def initialize
    @decision, @messages, @stored = 0, [], []
  end
  def pbStorePokemon(pokemon); @stored << pokemon; end
  def pbCaptureCalc(pokemon, battler, rate, ball); @received_rate = rate; end
  def pbEndOfRoundPhase; end
  def pbDisplay(message); @messages << message; end
end

class WildBattle
  class << self; attr_accessor :outcome, :crash, :capture_mismatch; end
  def self.start_core(*foes)
    if crash
      $player.party[0].hp = 1
      raise "Simulated engine fault"
    end
    result = outcome || 1
    if result == 4
      caught = foes.first
      caught.owner = {:name => "Engine reassignment"}
      caught.item = nil
      caught.name = "Engine rename"
      caught.instance_variable_set(:@tidebound_identity, "wrong") if capture_mismatch
      Battle.new.pbStorePokemon(caught)
    elsif [2, 5].include?(result)
      $player.party.each { |p| p.hp = 0 }
    end
    BattleCreationHelperMethods.after_battle(result, true)
    result
  end
end

def setBattleRule(*rules); $test_rules = rules; end
def _INTL(text); text; end

