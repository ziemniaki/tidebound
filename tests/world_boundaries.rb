# General world and battle operations must work without opening/necklace modules.
new_opening
$player.party << Pokemon.new(:NATU, 20, $player)
$quest_outcome = 1
opening = Tidebound.send(:remove_const, :Opening)
neighbor = Tidebound.send(:remove_const, :NeighborQuest)
begin
  Tidebound::World.travel(:road, 18, 5)
  check($game_map.map_id == 108, "named road transfer")
  event = OpeningEvent.new("Mother", 71)
  $game_map.events = { 71 => event }
  check(Tidebound::World.actor(:mother).equal?(event), "named actor lookup")
  $choices = [true]
  Tidebound::Pond.fisher(:toma)
  check(Tidebound::Pond.flags[:toma], "pond depends on an unrelated quest")
  Tidebound::World.travel(:docks, 11, 28)
  $choices = [true]
  Tidebound::DemoLaunch.sailor_battle(:nell)
  check(Tidebound::DemoLaunch.flags[:nell], "dock battle depends on an unrelated quest")
ensure
  Tidebound.const_set(:Opening, opening)
  Tidebound.const_set(:NeighborQuest, neighbor)
end
Tidebound::Opening.sync_opening_actors
puts "PASS: named world operations and pond/dock battles work without opening or necklace modules."

# Map entry synchronizes story actors even when no spriteset is constructed.
new_opening
Tidebound.story[:shop_unlocked] = true
Tidebound::VaultVisit.q[:open] = true
{ coast: :seller_outside, road: :road_thief, home: :mother }.each do |map, actor|
  $game_map.map_id = Tidebound::World::MAPS.fetch(map)
  event = OpeningEvent.new(Tidebound::World::ACTORS.fetch(actor), 72)
  event.through = false
  event.opacity = 255
  $game_map.events = { 72 => event }
  EventHandlers.trigger(:on_enter_map, 0)
  check(event.through && event.opacity == 0, "Map entry did not hide #{actor} without rendering")
end
