# Geometric ropes follow the same perimeter as the native blocking rail events.
# Two layers let the near rope sit in front of the sparring icons.
class TideboundRingRopes < Tidebound::Presentation::OwnedSprite
  def initialize(event, viewport, front)
    super(viewport)
    @event, @front = event, front
    self.bitmap = Bitmap.new(256, 200)
    wood = Color.new(82, 55, 43)
    light = Color.new(177, 144, 93)
    rope = Color.new(179, 160, 116)
    shadow = Color.new(48, 40, 39)
    ys = front ? [172] : [12]
    ys.each do |y|
      [0, 8].each do |drop|
        224.times do |x|
          sag = (Math.sin(x * Math::PI / 224) * 4).to_i
          self.bitmap.fill_rect(x + 16, y + sag + drop + 2, 1, 2, shadow)
          self.bitmap.fill_rect(x + 16, y + sag + drop, 1, 2, rope)
        end
      end
      [12, 236].each do |x|
        self.bitmap.fill_rect(x, y - 7, 8, 29, wood)
        self.bitmap.fill_rect(x, y - 7, 8, 3, light)
      end
    end
    unless front
      [14, 238].each do |x|
        self.bitmap.fill_rect(x + 2, 14, 2, 159, shadow)
        self.bitmap.fill_rect(x, 14, 2, 159, rope)
      end
    end
    update
  end

  def update
    super
    position_at_event(@event, dx: -16, dy: -32)
    self.z = @front ? @event.screen_z + 200 : @event.screen_z - 10
  end
end

class TideboundRingFighter < TideboundCompanionSprite
  def update
    super
    # Display-only lunges: no damage, encounters, save state or player movement.
    left = @actor.fetch("species") == "MACHOP"
    phase = (System.uptime + (left ? 0 : 1.5)) % 3.0
    lunge = phase < 0.35 ? Math.sin(phase / 0.35 * Math::PI) : 0
    self.x += (lunge * (left ? 22 : -22)).to_i
    self.y -= (lunge * 5).to_i
  end
end

EventHandlers.add(
  :on_new_spriteset_map,
  :tidebound_dock_ring,
  proc do |spriteset, viewport|
    spriteset.map.events.each_value do |event|
      actor = Tidebound::Actors.info(event)
      if actor["key"] == "dock_ring_corner"
        spriteset.addUserSprite(TideboundRingRopes.new(event, viewport, false))
        spriteset.addUserSprite(TideboundRingRopes.new(event, viewport, true))
      elsif actor["role"] == "dock_fighter"
        spriteset.addUserSprite(TideboundRingFighter.new(event, viewport))
      end
    end
  end
)
