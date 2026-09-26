# Ambient sparring: display copies only; no player Pokémon are mutated.
class TideboundRingFighter < PokemonIconSprite
  def initialize(event, viewport, species)
    @event = event
    @left = species == :MACHOP
    super(Pokemon.new(@left ? :MACHOP : :HITMONLEE, 20), viewport)
    setOffset(PictureOrigin::BOTTOM)
    self.mirror = !@left
    update
  end
  def update
    super
    # Alternate a short approach and recoil; leave a beat between blows.
    beat = System.uptime % 4.0
    phase = @left ? beat : (beat + 2.0) % 4.0
    lunge = phase < 0.35 ? Math.sin(phase / 0.35 * Math::PI) * 23 : 0
    self.x = @event.screen_x + (@left ? 64 : 160) + (@left ? lunge : -lunge)
    self.y = @event.screen_y + 96 - (lunge / 7).to_i
    self.z = @event.screen_z + 1
  end
end
EventHandlers.add(
  :on_new_spriteset_map,
  :tidebound_ring_fighters,
  proc do |spriteset, viewport|
    next unless spriteset.map.map_id == Tidebound::World::MAPS.fetch(:docks)
    spriteset.map.events.each_value do |event|
      next unless event.name == "Demo prop:quayring"
      %i[MACHOP HITMONLEE].each do |species|
        spriteset.addUserSprite(TideboundRingFighter.new(event, viewport, species))
      end
    end
  end
)
