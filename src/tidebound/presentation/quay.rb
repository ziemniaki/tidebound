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
    @sprites = Tidebound::Presentation::WINDOW_LIGHTS.fetch(map.map_id).map do |x, y, index|
      TideboundWindowPane.new(map, x, y, index, @atlas, @viewport)
    end
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

class TideboundQuayProp < Tidebound::Presentation::OwnedSprite
  def initialize(event, viewport)
    super(viewport)
    @event = event
    role = Tidebound::Actors.role(event)
    self.bitmap = Bitmap.new("Graphics/Pictures/Tidebound/#{role}")
    self.ox = role == "dock_boat" && event.x == 24 ? 96 : 32
    self.oy = 80
    update
  end
  def update
    super
    position_at_event(@event)
  end
end
EventHandlers.add(
  :on_new_spriteset_map,
  :tidebound_dock_details,
  proc do |spriteset, viewport|
    map = spriteset.map
    next unless [102, 108, 112].include?(map.map_id)
    spriteset.addUserSprite(TideboundWindowLights.new(map))
    if map.map_id == 112
      map.events.each_value do |e|
        if %w[dock_boat dock_bollard dock_nets dock_stall].include?(Tidebound::Actors.role(e))
          spriteset.addUserSprite(TideboundQuayProp.new(e, viewport))
        end
      end
    end
  end
)
