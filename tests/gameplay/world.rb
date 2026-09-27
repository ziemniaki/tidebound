# Pond and dock battles advance their own flags; actor lookup respects map ownership.
new_opening
$player.party << Pokemon.new(:NATU, 20, $player)
$quest_outcome = 1
Tidebound::World.travel(:road, 18, 5)
check($game_map.map_id == 108, "named road transfer")
check(Tidebound::World.actor(:mother).nil?, "wrong-map actor lookup must be absent")
Tidebound::World.travel(:home, 10, 12)
event = Tidebound::World.actor(:mother)
check(event && event.name != "Mother", "actor identity must ignore label")
Tidebound::World.travel(:road, 18, 5)
$choices = [true]
Tidebound::Pond.fisher(:toma)
check(Tidebound::Pond.flags[:toma], "pond depends on an unrelated quest")
Tidebound::World.travel(:docks, 11, 28)
$choices = [true]
Tidebound::DemoLaunch.sailor_battle(:nell)
check(Tidebound::DemoLaunch.flags[:nell], "dock battle depends on an unrelated quest")
Tidebound::Actors.refresh($game_map)
puts "PASS: named world operations and pond/dock battles preserve map ownership and quest progress."

# Map entry synchronizes story actors even when no spriteset is constructed.
new_opening
Tidebound.story[:shop_unlocked] = true
Tidebound::VaultVisit.q[:open] = true
{ coast: :seller_outside, road: :road_thief, home: :mother }.each do |map, actor|
  $game_map.map_id = Tidebound::World::MAPS.fetch(map)
  $game_map.events = world_events($game_map.map_id)
  event = Tidebound::World.actor(actor)
  event.through = false
  event.opacity = 255
  EventHandlers.trigger(:on_enter_map, 0)
  check(event.through && event.opacity == 0, "Map entry did not hide #{actor} without rendering")
end

# Resting visibility must not overwrite a scene's temporary actor state on a frame.
Tidebound::World.travel(:coast, 32, 36)
youth = Tidebound::World.actor(:robbery_youth_one)
youth.opacity = 255
youth.through = false
Tidebound::Actors.sync($game_map)
check(youth.opacity == 255 && !youth.through, "Frame sync hid a cutscene actor")
Tidebound::Scenes.run(youth) do
  Tidebound::Actors.refresh($game_map)
  check(youth.opacity == 255 && !youth.through, "Map refresh interrupted the robbery")
end
Tidebound::Actors.refresh($game_map)
check(youth.opacity == 0 && youth.through, "Scene actor did not return to its resting state")

# Conditional/computed routes are checked here; map validation cannot parse Ruby.
new_opening
Tidebound.story[:dream_room] = { phase: :folded }
Tidebound.story[:opening_started] = true
Tidebound::World.travel(:dream, 7, 8)
2.times do
  Tidebound::DreamRoom.arrival
  check([$game_map.map_id, $game_player.x, $game_player.y] == [116, 7, 22], "folded arrival/retry")
end
Tidebound.story[:dream_room][:phase] = :complete
Tidebound.story[:psychic_maze] = :active
Tidebound::DreamRoom.folded_arrival
check([$game_map.map_id, $game_player.x, $game_player.y] == [114, 5, 20], "return to active maze")
Tidebound.story[:psychic_maze] = :complete
Tidebound::DreamRoom.return_to_journey
check([$game_map.map_id, $game_player.x, $game_player.y] == [107, 6, 8], "return to bedroom")
puts "PASS: conditional dream/folded-room arrival, retry and both return routes."

# Native encounter callers use a Boolean result, not Ruby-truthy outcome codes.
new_opening
Tidebound::World.travel(:road, 18, 5)
original_fight = Tidebound::Encounters.method(:fight)
begin
  {
    0 => true,
    1 => true,
    2 => false,
    3 => true,
    4 => true,
    5 => false,
    :astral => false
  }.each do |outcome, expected|
    Tidebound::Encounters.define_singleton_method(:fight) { |*foes| outcome }
    result = WildBattle.start(:ZUBAT, 5, can_override: true)
    check(result == expected, "WildBattle.start returned #{result.inspect} for #{outcome}")
  end
ensure
  Tidebound::Encounters.define_singleton_method(:fight, original_fight)
end
puts "PASS: native grass encounters preserve the engine's Boolean result contract."
