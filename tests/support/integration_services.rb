# Services outside the headless integration boundary. Production scripts load whole.
# The real SaveData codec and registration code have already been loaded.
["frame_count", "game_system", "pokemon_system", "switches", "variables", "self_switches", "game_screen", "map_factory", "game_player", "global_metadata", "map_metadata", "storage_system", "essentials_version", "game_version", "stats"].each { |name| SaveData.unregister(name.to_sym) }

class Sprite; end
class PokemonIconSprite < Sprite; end
class Game_System; end
class Scene_Map; end
class PokemonEncounters; end
module Game; end
class WildBattle; end
module Input
  def self.update; end
end
module Graphics
  def self.width; 640; end
  def self.height; 480; end
end
class Game_Map
  TILE_WIDTH = 32
  TILE_HEIGHT = 32
  REAL_RES_X = 128
  REAL_RES_Y = 128
  attr_accessor :display_x, :display_y
  def width; 80; end
  def height; 80; end
  def autoplay; end
end
class OpeningEvent
  attr_accessor :character_name
  def turn_toward_player; end
end
def pbReceiveItem(item)
  $bag.add(item)
end
class Game_Map
  def display_x; @display_x || 0; end
  def display_y; @display_y || 0; end
end
