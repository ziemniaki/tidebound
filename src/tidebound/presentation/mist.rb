# Coastal mist crosses the darkness field, so its shape remains visible at night.
# Native planes scroll a shared texture; no pixels are regenerated each frame.
class Tidebound::Presentation::CoastalMist
  # Horizontal/vertical scale, wind pixels/sec, maximum opacity, density period.
  LAYERS = [[1.4, 1.1, 7, 0.8, 72, 24], [2.0, 1.6, 3, -0.4, 32, 37]].freeze

  def initialize(map)
    @map = map
    @settings = Tidebound::World::MAP_SETTINGS.fetch(map.map_id)
    @started = System.uptime
    @viewport = Viewport.new(0, 0, Graphics.width, Graphics.height)
    @viewport.z = 3
    @bitmap = Bitmap.new("Graphics/Fogs/coastal_mist")
    @planes =
      LAYERS.map do |sx, sy, _vx, _vy, _opacity, _period|
        plane = Plane.new(@viewport)
        plane.bitmap = @bitmap
        # Keep cloud banks at world scale independently of source-image resolution.
        plane.zoom_x = sx * 512.0 / @bitmap.width
        plane.zoom_y = sy * 512.0 / @bitmap.height
        plane.tone = Tone.new(-20, -20, -18, 0)
        plane
      end
    update
  end

  def update
    return if disposed?
    @viewport.visible = @map.map_id == $game_map.map_id
    return unless @viewport.visible
    @viewport.rect.set(0, 0, Graphics.width, Graphics.height)
    @viewport.ox = $game_screen.shake
    elapsed = System.uptime - @started
    entry = [elapsed / 1.5, 1].min
    entry = entry * entry * (3 - 2 * entry)
    density_scale = @settings.fetch(:opacity) / 150.0
    direction = @settings.fetch(:speed)
    ox = @map.display_x / Game_Map::X_SUBPIXELS
    oy = @map.display_y / Game_Map::Y_SUBPIXELS
    @planes.each_with_index do |plane, i|
      _sx, _sy, vx, vy, opacity, period = LAYERS[i]
      phase = elapsed + (@map.map_id % 7) * 3 + i * 11
      bank = (1 - Math.cos(phase * 2 * Math::PI / period)) / 2
      density = 0.2 + 0.8 * bank * bank
      plane.opacity = (opacity * density_scale * density * entry).round
      plane.ox = (ox + elapsed * vx * direction + i * 217).round
      plane.oy = (oy + elapsed * vy + i * 113).round
    end
  end

  def disposed?
    !!@disposed
  end

  def dispose
    return if disposed?
    @planes.each(&:dispose)
    @bitmap.dispose
    @viewport.dispose
    @disposed = true
  end
end

EventHandlers.add(
  :on_new_spriteset_map,
  :tidebound_coastal_mist,
  proc do |spriteset, _viewport|
    if Tidebound::World::MAP_SETTINGS[spriteset.map.map_id]&.fetch(:fog) == "coastal_mist"
      spriteset.addUserSprite(Tidebound::Presentation::CoastalMist.new(spriteset.map))
    end
  end
)
