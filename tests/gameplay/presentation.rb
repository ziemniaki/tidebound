def check(value, message)
  raise message unless value
end
viewport = Resource.new
bitmap = Resource.new
sprite = Tidebound::Presentation::OwnedSprite.new(viewport)
sprite.bitmap = bitmap
sprite.dispose
sprite.dispose
check(bitmap.disposals == 1, "Owned bitmap must be disposed exactly once")
check(viewport.disposals == 0, "Shared viewport must remain alive")
owned = Resource.new
sprite = Tidebound::Presentation::OwnedSprite.new(owned, owns_viewport: true)
sprite.dispose
sprite.dispose
check(owned.disposals == 1, "Owned viewport must be disposed exactly once")

event = Struct.new(:screen_x, :screen_y, :screen_z).new(100, 200, 3)
sprite = Tidebound::Presentation::OwnedSprite.new(viewport)
sprite.position_at_event(event, dx: -16, dy: 5, dz: 1)
check([sprite.x, sprite.y, sprite.z] == [84, 205, 4], "Event positioning")
map = Game_Map.new
map.display_x = 16
map.display_y = 32
sprite.position_at_tile(map, 3, 4, dx: 16, dy: 32)
check([sprite.x, sprite.y] == [108, 152], "Tile positioning")

# No sprite is allocated for these actors: gameplay collision must still update.
actor = Struct.new(:name, :through, :move_route_forcing, :map_id, :id)
forest = Tidebound::World::ACTOR_SETTINGS.fetch(103)
keys_id = forest.find { |_id, info| info["role"] == "keys" }.first
bird_id = forest.find { |_id, info| info["role"] == "wood_bird" }.first
keys = actor.new("A renamed key", false, false, 103, keys_id)
bird = actor.new("A renamed bird", false, false, 103, bird_id)
# A misleading prefix cannot opt an unregistered event into story policy.
ordinary = actor.new("Wild:NATU", false, false, 103, 999)
map.map_id = 103
map.events = { keys_id => keys, bird_id => bird, 999 => ordinary }
Tidebound.story[:keys_collected] = true
Tidebound.story[:wood_bird_gone] = true
map.update
check(keys.through && bird.through && !ordinary.through, "Headless actor collision")
Tidebound.story.clear
map.update
check(!keys.through && !bird.through, "Visible actors block movement")
keys.move_route_forcing = true
Tidebound.story[:keys_collected] = true
map.update
check(!keys.through, "Scripted route retains collision ownership")
puts "PASS: sprite resources, positioning and collision without rendering"
