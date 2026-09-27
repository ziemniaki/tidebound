# Services outside the headless integration boundary. Production scripts load whole.
# The real SaveData codec and registration code have already been loaded.
%w[
  frame_count
  game_system
  pokemon_system
  switches
  variables
  self_switches
  game_screen
  map_factory
  game_player
  global_metadata
  map_metadata
  storage_system
  essentials_version
  game_version
  stats
].each { |name| SaveData.unregister(name.to_sym) }

class Sprite
  def update
  end
end
class PokemonIconSprite < Sprite
end
class Game_System
end
class Scene_Map
end
class PokemonEncounters
end
module Game
end
class WildBattle
end
module Input
  def self.update
  end
end
module Graphics
  def self.width
    640
  end
  def self.height
    480
  end
end
class Game_Map
  TILE_WIDTH = 32
  TILE_HEIGHT = 32
  REAL_RES_X = 128
  REAL_RES_Y = 128
  attr_accessor :display_x, :display_y
  def width
    80
  end
  def height
    80
  end
  def autoplay
  end
end
class OpeningEvent
  attr_accessor :character_name
  def turn_toward_player
  end
end
def pbReceiveItem(item, quantity = 1)
  $bag.add(item, quantity)
end
class Game_Map
  def display_x
    @display_x || 0
  end
  def display_y
    @display_y || 0
  end
end

# Native Essentials objects/save codec; battle outcomes and scene services mocked.
class TrainerBattle
  def self.start_core(foe)
    raise "not NPC trainer" unless foe.is_a?(NPCTrainer) && !foe.party.empty?
    if [2, 5].include?($quest_outcome)
      $player.party.each { |p| p.hp = 0 }
      Tidebound.before_cleanup_party = Tidebound.copy($player.party)
      $player.party.each(&:heal)
    end
    $quest_outcome
  end
end
def setBattleRule(*rules)
  $quest_rules = rules
end

class PokemonBag
  alias quest_original_add add
  def add(item, *args)
    return false if item == $quest_reject_item
    quest_original_add(item, *args)
  end
end
