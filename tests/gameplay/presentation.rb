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

puts "PASS: sprite resources and positioning"
