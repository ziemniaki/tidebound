# A failed cutscene releases actors and restores temporary presentation, not quest progress.
new_opening
Tidebound::World.travel(:home, 10, 12)
mother = Tidebound::World.actor(:mother)
mother.opacity, mother.through, mother.move_speed = 255, false, 3
original = [mother.x, mother.y, mother.direction]
begin
  Tidebound::Scenes.run(mother, restore_positions: true) do
    mother.moveto(1, 1)
    mother.opacity, mother.through, mother.move_speed = 0, true, 6
    Tidebound::World.camera_target = mother
    Tidebound.story[:scene_test_progress] = true
    raise "Interrupted scene"
  end
rescue RuntimeError => error
  raise unless error.message == "Interrupted scene"
end
check([mother.x, mother.y, mother.direction] == original, "Interrupted scene displaced its actor")
check(
  mother.opacity == 255 && !mother.through && mother.move_speed == 3,
  "Leaked scene presentation"
)
check(!Tidebound::Scenes.owns?(mother) && !Tidebound::World.camera_target, "Leaked scene ownership")
check(Tidebound.story[:scene_test_progress], "Scene cleanup rewrote story progress")

# Frame collision updates work without rendering and leave scene-owned actors alone.
Tidebound::World.travel(:forest, 17, 25)
key_id = Tidebound::World::ACTOR_SETTINGS.fetch(103).find { |_id, a| a["role"] == "keys" }.first
keys = $game_map.events.fetch(key_id)
keys.through = false
Tidebound.story[:keys_collected] = true
Tidebound::Scenes.run(keys) do
  Tidebound::Actors.sync($game_map)
  check(!keys.through, "Frame sync took collision from a scene")
end
check(keys.through, "Scene exit did not restore current story collision")
puts "PASS: interrupted scene cleanup, actor ownership and headless collision"

%i[road_thief nonexistent_actor].each do |key|
  rejected = false
  begin
    Tidebound::Actors.on_entry(key) { true }
  rescue RuntimeError
    rejected = true
  end
  check(rejected, "Duplicate/unknown actor policy was accepted: #{key}")
end
