# The compiler supplies glass masks and their tile positions; this code only places sprites.
class TideboundWindowPane < Sprite
  include Tidebound::Presentation::Position
  def initialize(map, x, y, index, atlas, viewport)
    super(viewport)
    @map, @tx, @ty = map, x, y
    self.bitmap = atlas
    self.src_rect.set(index * 32, 0, 32, 32)
    update
  end
  def update
    super
    position_at_tile(@map, @tx, @ty)
  end
end

class TideboundWindowLights
  def disposed?
    !!@disposed
  end
  def initialize(map)
    @viewport = Viewport.new(0, 0, Graphics.width, Graphics.height)
    @viewport.z = 1
    @atlas = Bitmap.new("Graphics/Pictures/Tidebound/window_panes")
    @sprites =
      Tidebound::Presentation::WINDOW_LIGHTS
        .fetch(map.map_id)
        .map { |x, y, index| TideboundWindowPane.new(map, x, y, index, @atlas, @viewport) }
  end
  def update
    @sprites.each(&:update)
  end
  def dispose
    return if disposed?
    @sprites.each(&:dispose)
    @atlas.dispose
    @viewport.dispose
    @disposed = true
  end
end

# The same local light used by sheltered lamps, reduced to a candle-sized spill.
class TideboundVotiveLight < TideboundWarmLight
  def initialize(map, event)
    @phase = event.id
    super(map, event.x, event.y)
    self.zoom_x = self.zoom_y = 0.32
  end

  def update
    super
    self.x -= 18
    self.y -= 20
    self.opacity = 140 + (Math.sin(System.uptime * 2.7 + @phase) * 18).to_i
  end
end

EventHandlers.add(
  :on_new_spriteset_map,
  :tidebound_dock_details,
  proc do |spriteset, viewport|
    map = spriteset.map
    map.events.each_value do |event|
      next unless Tidebound::Actors.info(event)["asset"] == "votive_offerings"
      spriteset.addUserSprite(TideboundVotiveLight.new(map, event))
    end
    next unless Tidebound::Presentation::WINDOW_LIGHTS.key?(map.map_id)
    spriteset.addUserSprite(TideboundWindowLights.new(map))
  end
)
