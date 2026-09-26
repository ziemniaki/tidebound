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
actor = Struct.new(:name, :through, :move_route_forcing)
keys = actor.new("Shop keys", false, false)
bird = actor.new("Wild:NATU", false, false)
crate = actor.new("Crate 1", true, false)
map.map_id = 103
map.events = { 1 => keys, 2 => bird, 3 => crate }
Tidebound.story[:keys_collected] = true
Tidebound.story[:wood_bird_gone] = true
map.update
check(keys.through && bird.through && !crate.through, "Headless actor collision")
Tidebound.story.clear
map.update
check(!keys.through && !bird.through, "Visible actors block movement")
keys.move_route_forcing = true
Tidebound.story[:keys_collected] = true
map.update
check(!keys.through, "Scripted route retains collision ownership")
puts "PASS: sprite resources, positioning and collision without rendering"
