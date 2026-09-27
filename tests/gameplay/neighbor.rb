n = Tidebound::NeighborQuest
o = Tidebound::Opening
h = Tidebound::Hideout
new_opening
Tidebound.story.merge!(walk_state: :complete, hall_talk: true)
$choices = [true]
o.house_pet(:NATU)
Tidebound.story[:shop_unlocked] = true
Tidebound::World.travel(:shop, 8, 10)
Tidebound::Interactions.oil_seller
Tidebound::Interactions.oil_seller
check(n.stage == :pie && $bag.quantity(n::PIE) == 1, "pie absent/duplicated")
[n::PIE, n::PLATE, n::NECKLACE].each do |i|
  d = GameData::Item.get(i)
  check(d.is_key_item? && d.field_use == 0 && d.battle_use == 0, "healing/key item")
end
roundtrip
Tidebound::World.travel(:home, 10, 12)
Tidebound::Interactions.mother
check(
  Tidebound.story[:oil_returned] && n.stage == :plate && $bag.has?(n::PLATE) && !$bag.has?(n::PIE),
  "meal"
)
Tidebound::Interactions.mother
check($bag.quantity(n::PLATE) == 1, "repeat meal")
o.main_lamp
roundtrip
Tidebound::World.travel_coast(21, 12)
Tidebound::Interactions.shop_door
check(n.stage == :pursuit && !$bag.has?(n::PLATE), "robbery")
n.robbery
roundtrip
n.south_gate
check($game_map.map_id == 108, "south door")
$quest_outcome = 2
n.first_thief
check(Tidebound.state.realm == :astral && $player.party.empty? && !n.q[:first_won], "loss advances")
check(Tidebound.state.souls.last.pokemon.hp == 0, "snapshot after heal")
check($quest_rules.include?("canLose") && $quest_rules.include?("noMoney"), "rules")
roundtrip
point = Tidebound.return_to_living!
Tidebound::World.travel(*point)
Tidebound::World.travel(:road, 26, 23)
$quest_outcome = 1
n.first_thief
check(n.q[:first_won], "first win")
roundtrip
n.witness_hideout
n.hideout_door
h.arrival
check(n.q[:heard] && $game_map.map_id == 109, "hideout")
$quest_outcome = 0
h.boss
check(!n.q[:runner_won] && !n.q[:second_won], "cancelled guard advances")
$quest_outcome = 5
h.guard
check(!n.q[:runner_won] && n.stage == :pursuit, "draw advances")
point = Tidebound.return_to_living!
Tidebound::World.travel(*point)
Tidebound::World.travel(:hideout, 11, 14)
$quest_outcome = 1
h.guard
$hideout_result = false
h.boss
check(!n.q[:hideout_game_won] && !n.q[:second_won], "cancelled minigame advances")
$hideout_result = true
h.boss
check(n.stage == :necklace && n.q[:hideout_game_won] && $bag.quantity(n::NECKLACE) == 1, "recovery")
h.boss
roundtrip
Tidebound::World.travel(:shop, 8, 10)
Tidebound::Interactions.oil_seller
check(n.stage == :complete && !$bag.has?(n::NECKLACE), "return")
Tidebound::Interactions.oil_seller
roundtrip
check([n::PIE, n::PLATE, n::NECKLACE].none? { |i| $bag.has?(i) }, "duplicated rewards")
check(Tidebound.story[:lamp_lit] && o.household_pets.size == 2, "old progress reset")
puts "PASS: Necklace quest; saved stages; trainer loss/draw/retry; unique items; preserved household."
new_opening
Tidebound.story.merge!(
  {
    starter_chosen: :MAKUHITA,
    walk_state: :complete,
    hall_talk: true,
    oil_requested: true,
    oil_collected: true,
    oil_returned: true,
    lamp_lit: true,
    shop_unlocked: true
  }
)
Tidebound::World.travel(:shop, 8, 10)
Tidebound::Interactions.oil_seller
check(n.stage == :pie && Tidebound.story[:lamp_lit], "completed oil quest")
Tidebound::World.travel(:home, 10, 12)
$quest_reject_item = n::PLATE
n.meal
check(n.stage == :pie && $bag.has?(n::PIE), "full bag consumes pie")
$quest_reject_item = nil
n.meal
puts "PASS: completed-oil save and full-bag meal rollback."
