# The pier is reachable before Pookie's walk, including repeated visits.
new_opening
Tidebound::World.travel_coast(44, 20)
Tidebound::Opening.pier
check(Tidebound.story[:pier_seen] && !Tidebound.story[:lapras_glimpsed], "early apparition")
messages = $messages.size
Tidebound::Opening.pier
check($messages.size == messages && $player.party.empty?, "early pier changed progress")
puts "PASS: pier interaction before Pookie's walk, including repeat visit."

o = Tidebound::Opening
%i[NATU MAKUHITA POOCHYENA].each_with_index do |species, index|
  new_opening
  check($game_map.events[1].erased, "autorun")
  check($player.party.empty?, "early party")
  ids = o.household_pets.values.map { |p| Tidebound.identity(p) }
  o.begin_story
  check(
    ids.uniq.size == 3 && o.household_pets.values.map { |p| Tidebound.identity(p) } == ids,
    "pet identity reroll"
  )
  o.house_pet(species)
  check($player.party.empty?, "early choice")
  o.forest_gate
  check($game_map.map_id != 103, "early forest")
  walk(index == 1)
  check(!!Tidebound.story[:walk_pier_seen] == (index == 1), "pier was mandatory/repeated")
  check(!Tidebound.story[:lamp_lit] && !Tidebound.story[:oil_requested], "oil precedes choice")
  $choices = [false]
  o.house_pet(species)
  check($player.party.empty?, "cancel chose pet")
  chosen = o.household_pets[species]
  id = Tidebound.identity(chosen)
  $player.name = "Test Ren"
  $choices = [true]
  o.house_pet(species)
  check(
    $player.party == [chosen] && chosen.owner.name == "Test Ren" &&
      Tidebound.identity(chosen) == id,
    "wrong individual"
  )
  check(
    o.household_pets.size == 2 && $bag.quantity(:POKEBALL) == 8 && Tidebound.story[:oil_requested],
    "selection supplies/oil"
  )
  o::HOUSE_PETS.each_key { |s| o.house_pet(s) }
  check($player.party.size == 1 && $bag.quantity(:POKEBALL) == 8, "duplicate starter/supplies")
  Tidebound::World.travel_coast(21, 12)
  Tidebound::Interactions.shop_door
  check($game_map.map_id == 102, "shop unlocked early")
  Tidebound::Interactions.outside_seller
  check(Tidebound.story[:keys_requested], "keys quest absent")
  Tidebound::Interactions.oil_seller
  check(!Tidebound.story[:oil_collected], "oil outside")
  o.forest_gate
  check($game_map.map_id == 103, "forest requires lamp")
  o.forest_keys
  o.forest_keys
  check($bag.quantity(:TIDEBOUNDOILKEYS) == 1, "missing/duplicate keys")
  check(GameData::Item.get(:TIDEBOUNDOILKEYS).is_key_item?, "not a Key Item")
  roundtrip
  check($bag.has?(:TIDEBOUNDOILKEYS), "keys not saved")
  Tidebound::World.travel_coast(21, 12)
  Tidebound::Interactions.outside_seller
  check(Tidebound.story[:shop_unlocked] && !$bag.has?(:TIDEBOUNDOILKEYS), "unlock exchange")
  Tidebound::Interactions.outside_seller
  check(!Tidebound.story[:oil_collected], "oil without entering")
  Tidebound::Interactions.shop_door
  check($game_map.map_id == 106, "shop didn't open")
  Tidebound::Interactions.oil_seller
  Tidebound::World.travel(:home, 10, 12)
  Tidebound::Interactions.mother
  o.main_lamp
  check(Tidebound.story[:lamp_lit], "oil/lamp continuation")
  puts "PASS: #{species}; #{index == 1 ? "optional pier" : "no pier"}; 99/100 steps, return, identity, keys/save/unlock/oil."
end

new_opening
walk
$choices = [true]
o.house_pet(:MAKUHITA)
o.forest_gate
$choices = [0]
o.fire
check(Tidebound.state.checkpoint == [103, 11, 22, 8], "checkpoint")
Tidebound.state.enter_astral!($player.party, { map_id: 103 })
$player.party.clear
$game_map.map_id = 105
Tidebound::Astral.arrival
Tidebound::Astral.arrival
check($player.party.size == 1 && Tidebound.borrowed?($player.party.first), "guide duplication")
roundtrip
check(Tidebound.state.waiting_ids.size == 1, "saved soul")
$choices = [true]
Tidebound::Astral.leave
check($game_map.map_id == 103 && Tidebound.state.memorials.size == 1, "return/loss")
o.house_pet(:POOCHYENA)
check($player.party.size == 1, "replacement starter after death")
puts "PASS: chosen Makuhita loss, rest, guide, real SaveData and no replacement starter."

%i[egg borrowed].each do |kind|
  new_opening
  companion = Pokemon.new(:NATU, 7, $player)
  companion.steps_to_hatch = 1 if kind == :egg
  companion.instance_variable_set(:@tidebound_borrowed, true) if kind == :borrowed
  $player.party = [companion]
  $messages.clear
  Tidebound::FieldDetails.rest(:unhealable_test, [101, 6, 10, 2])
  check(
    $messages == ["You warm your hands beside the fire."],
    "unhealable party reported a cooldown"
  )
  check(
    Tidebound::FieldDetails.remaining(:unhealable_test) == 0,
    "unhealable rest consumed cooldown"
  )
end
puts "PASS: egg-only and borrowed-only parties do not receive impossible fire cooldown advice."
