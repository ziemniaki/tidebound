# Exercise the final shared-NPC dispatch rather than a prepend chain.
new_opening
n = Tidebound::NeighborQuest
v = Tidebound::VaultVisit
i = Tidebound::Interactions
n.q[:stage] = :complete
Tidebound::World.travel(:shop, 8, 10)
i.oil_seller
check(v.q[:gift] && $bag.quantity(v::GIFT) == 1, "vault reward missing")
i.oil_seller
check($bag.quantity(v::GIFT) == 1, "vault reward repeated")
Tidebound::World.travel(:home, 10, 12)
i.mother
check(v.q[:open], "mother did not open vault after the gift")
v.q[:museum] = true
i.mother
check($messages.last.include?("Did you find the museum?"), "museum dialogue lost precedence")
check(i.hint == v.hint, "journal does not prefer the current chapter")
puts "PASS: explicit shared-NPC dispatch, unique vault gift, mother and journal chapter precedence."

# Harvest keys use authored local coordinates; the coast alone has an origin offset.
# Read saved harvest state through the production visual, including after reload.
new_opening
[[102, 12, 18], [103, 12, 19], [108, 20, 54]].each do |map, x, y|
  before = $bag.quantity(:ORANBERRY)
  Tidebound::FieldDetails.berry(map, x, y, :ORANBERRY)
  check($bag.quantity(:ORANBERRY) == before + 2, "berry harvest missing")
  roundtrip
  event = OpeningEvent.new
  ox, oy = Tidebound::World::MAP_SETTINGS.fetch(map).fetch(:origin)
  event.moveto(x + ox, y + oy)
  visual = TideboundBerryVisual.allocate
  visual.instance_variable_set(:@event, event)
  visual.instance_variable_set(:@map_id, map)
  visual.update
  check(event.direction == 4, "harvested berries appear ripe on map #{map}")
  Tidebound::FieldDetails.berry(map, x, y, :ORANBERRY)
  check($bag.quantity(:ORANBERRY) == before + 2, "harvest repeated before regrowth")
  Tidebound.story[:berry_picks][[map, x, y]] -= Tidebound::FieldDetails::BERRY_SECONDS
  visual.update
  check(event.direction == 8, "berries did not visibly regrow on map #{map}")
end
puts "PASS: berry harvest, saved appearance and regrowth on coast, forest and road."
