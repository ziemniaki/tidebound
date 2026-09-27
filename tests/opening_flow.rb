# IDs and map ownership match generated data; labels deliberately do not.
def world_events(map_id)
  events = { 1 => OpeningEvent.new }
  (Tidebound::World::ACTOR_SETTINGS[map_id] || {}).each do |id, _info|
    events[id] = OpeningEvent.new("Fixture label #{id}", id)
  end
  events.each_value { |event| event.map_id = map_id }
  events
end

# Real Essentials Pokemon, bag and SaveData; graphics/movement have fixtures here.
# Full native movement and rendering are separately checked in rendered_smoke.rb.
def check(value, label)
  raise label unless value
end
def new_opening
  SaveData.mark_values_as_unloaded
  $messages.clear
  $choices.clear
  $game_map = Game_Map.new
  $game_map.map_id = 107
  $game_map.events = world_events($game_map.map_id)
  $game_player = OpeningPlayerLocation.new
  $opening_interpreter = Interpreter.allocate
  $opening_interpreter.instance_variable_set(:@event_id, 1)
  $PokemonGlobal = OpeningGlobal.new
  $scene = OpeningScene.new
  $bag = PokemonBag.new
  $player = Player.new("Unnamed", :POKEMONTRAINER_Red)
  $tidebound = Tidebound::State.new
  $stats = Struct.new(:distance_walked).new(0)
  Followers.remove("Tidebound Pookie")
  Tidebound::Opening.begin_story
end
def walk_step_fixture
  $stats.distance_walked += 1
  Tidebound::Opening.walk_step
end

def roundtrip
  saved = Marshal.load(Marshal.dump(SaveData.compile_save_hash))
  $tidebound = nil
  $player = nil
  $bag = nil
  SaveData.mark_values_as_unloaded
  SaveData.load_all_values(saved)
end
def walk(pier = false)
  o = Tidebound::Opening
  o.bedroom_pet
  o.bedroom_exit
  o.home_arrival
  Tidebound::World.travel_coast(8, 16)
  o.pookie
  if pier
    $game_player.moveto(*Tidebound::World.coast_xy(34, 20))
    walk_step_fixture
    o.pier_run
    check(Tidebound.story[:walk_state] == :at_pier, "dog didn't run")
    before = Tidebound.story[:walk_steps]
    10.times { walk_step_fixture }
    check(Tidebound.story[:walk_steps] == before, "unaccompanied steps count")
    roundtrip
    Tidebound::World.travel(:home, 10, 12)
    o.home_arrival
    check(Tidebound.story[:walk_state] == :at_pier, "left dog at pier")
    Tidebound::World.travel_coast(44, 20)
    o.pookie
  end
  $game_player.moveto(*Tidebound::World.coast_xy(8, 18))
  (99 - Tidebound.story[:walk_steps]).times { walk_step_fixture }
  Tidebound::World.travel(:home, 10, 12)
  o.home_arrival
  check(Tidebound.story[:walk_state] == :following, "walk completed at 99")
  5.times { walk_step_fixture }
  check(Tidebound.story[:walk_steps] == 99, "indoor steps count")
  Tidebound::World.travel_coast(8, 18)
  walk_step_fixture
  check(Tidebound.story[:walk_steps] == 100, "100th step missing")
  roundtrip
  Tidebound::World.travel(:home, 10, 12)
  o.home_arrival
  check(
    Tidebound.story[:walk_state] == :complete && !Followers.get(o::POOKIE_FOLLOWER),
    "home completion/follower cleanup"
  )
end

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
o.astral_arrival
o.astral_arrival
check($player.party.size == 1 && Tidebound.borrowed?($player.party.first), "guide duplication")
roundtrip
check(Tidebound.state.waiting_ids.size == 1, "saved soul")
$choices = [true]
o.return_from_astral
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
