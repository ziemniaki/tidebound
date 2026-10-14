# Exercise the actual light field without a graphics double.
new_opening
field = Tidebound::Lighting::Field.new(64, 64, { "ambient" => 20 })
source = { "radius" => 2, "strength" => 0.8, "color" => [255, 180, 90] }
alpha = proc { |pixels, x, y| pixels[0].getbyte((y * 64 + x) * 4 + 3) }
empty = field.render(0, 0, [])
lit = field.render(0, 0, [[:lamp, 128, 128, source, 0.8]])
raise "Light does not reveal scenery" unless alpha.call(lit, 32, 32) < alpha.call(empty, 32, 32)
raise "Light reaches beyond its radius" unless alpha.call(lit, 0, 0) == alpha.call(empty, 0, 0)
unless lit[1].getbyte((32 * 64 + 32) * 4) > lit[1].getbyte((32 * 64 + 32) * 4 + 2)
  raise "Flame has no warm tint"
end
overlap = field.render(0, 0, [[:a, 128, 128, source, 0.8], [:b, 128, 128, source, 0.8]])
unless alpha.call(overlap, 32, 32) < alpha.call(lit, 32, 32)
  raise "Overlapping lights darken each other"
end
raise "Opaque wall leaks" unless Tidebound::Lighting.blocked?(1, 3, 7, 3, [[4, 1, 1, 5]])
if Tidebound::Lighting.blocked?(1, 0, 7, 0, [[4, 1, 1, 5]])
  raise "Ray parallel to wall blocked incorrectly"
end
wall = Tidebound::Lighting::Field.new(64, 64, { "ambient" => 20, "blockers" => [[4, 0, 1, 8]] })
blocked = wall.render(0, 0, [[:lamp, 96, 128, { "radius" => 5 }, 1]])
unless alpha.call(blocked, 48, 32) == alpha.call(empty, 48, 32)
  raise "Light renders through blocker"
end
fade =
  Tidebound::Lighting::Field.new(
    1,
    1,
    { "ambient" => 40, "north_fade" => { "from_y" => 40, "to_y" => 10, "ambient" => 10 } }
  )
unless fade.ambient(10 * 32) < fade.ambient(25 * 32) &&
         fade.ambient(25 * 32) < fade.ambient(40 * 32)
  raise "North fails to get darker"
end
puts "PASS: local illumination, falloff, warm tint, overlap, walls and north gradient"
