class Sprite
  attr_accessor :bitmap, :x, :y, :z
  def initialize(viewport)
    @disposed = false
  end
  def disposed?
    @disposed
  end
  def dispose
    @disposed = true
  end
end
class Resource
  attr_reader :disposals
  def initialize
    @disposals = 0
  end
  def disposed?
    @disposals > 0
  end
  def dispose
    @disposals += 1
  end
end
class Game_Map
  REAL_RES_X = REAL_RES_Y = 128
  X_SUBPIXELS = Y_SUBPIXELS = 4
  attr_accessor :events, :map_id, :display_x, :display_y
  def update
  end
end
module Tidebound
  def self.story
    @story ||= {}
  end
  module World
    MAP_IDS = [101, 102, 103]
  end
end
