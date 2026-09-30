module Tidebound::Presentation
  module Position
    def position_at_event(event, dx: 0, dy: 0, dz: 0)
      self.x = event.screen_x + dx
      self.y = event.screen_y + dy
      self.z = event.screen_z + dz
    end

    def position_at_tile(map, x, y, dx: 0, dy: 0)
      self.x = (x * Game_Map::REAL_RES_X - map.display_x) / Game_Map::X_SUBPIXELS + dx
      self.y = (y * Game_Map::REAL_RES_Y - map.display_y) / Game_Map::Y_SUBPIXELS + dy
    end
  end

  # Own allocated or independently loaded bitmaps; never borrowed cache images.
  class OwnedSprite < Sprite
    include Position

    def initialize(viewport, owns_viewport: false)
      super(viewport)
      @owned_viewport = viewport if owns_viewport
    end

    def load_prop(name)
      asset = PROP_ASSETS.fetch(name)
      bitmap.dispose if bitmap && !bitmap.disposed?
      self.bitmap = Bitmap.new("Graphics/Pictures/#{asset.fetch("file")}")
      self.ox, self.oy = asset.fetch("anchor")
      self.zoom_x = self.zoom_y = asset.fetch("scale", 1)
    end

    def dispose
      return if disposed?
      bitmap.dispose if bitmap && !bitmap.disposed?
      super
      @owned_viewport.dispose if @owned_viewport && !@owned_viewport.disposed?
    end
  end
end
