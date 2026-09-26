# Real Essentials Pokemon, bag and SaveData; graphics/movement have fixtures here.
# Full native movement and rendering are separately checked in rendered_smoke.rb.
def check(value, label); raise label unless value; end
def new_opening
  SaveData.mark_values_as_unloaded
  $messages.clear; $choices.clear
  $game_map=Game_Map.new; $game_map.map_id=107
  $game_map.events={1=>OpeningEvent.new, 2=>OpeningEvent.new("Pookie outside",2),
    3=>OpeningEvent.new("Mother visiting",3), 4=>OpeningEvent.new("Seller outside",4)}
  $game_player=OpeningPlayerLocation.new
  $opening_interpreter=Interpreter.allocate
  $opening_interpreter.instance_variable_set(:@event_id,1)
  $PokemonGlobal=OpeningGlobal.new; $scene=OpeningScene.new
  $bag=PokemonBag.new; $player=Player.new("Unnamed",:POKEMONTRAINER_Red)
  $tidebound=Tidebound::State.new
  $stats=Struct.new(:distance_walked).new(0)
  Followers.remove("Tidebound Pookie")
  Tidebound::Opening.begin_story
end
def walk_step_fixture
  $stats.distance_walked+=1
  Tidebound::Opening.walk_step
end

def roundtrip
  saved=Marshal.load(Marshal.dump(SaveData.compile_save_hash))
  $tidebound=nil; $player=nil; $bag=nil
  SaveData.mark_values_as_unloaded; SaveData.load_all_values(saved)
end
def walk(pier=false)
  o=Tidebound::Opening
  o.bedroom_pet; o.bedroom_exit; o.home_arrival
  o.travel_coast(8,16); o.pookie
  if pier
    $game_player.moveto(*o.coast_xy(34,20)); walk_step_fixture; o.pier_run
    check(o.flags[:walk_state]==:at_pier,"dog didn't run")
    before=o.flags[:walk_steps]; 10.times {walk_step_fixture}
    check(o.flags[:walk_steps]==before,"unaccompanied steps count")
    roundtrip
    o.travel(101,10,12); o.home_arrival
    check(o.flags[:walk_state]==:at_pier,"left dog at pier")
    o.travel_coast(44,20); o.pookie
  end
  $game_player.moveto(*o.coast_xy(8,18))
  (99-o.flags[:walk_steps]).times { walk_step_fixture }
  o.travel(101,10,12); o.home_arrival
  check(o.flags[:walk_state]==:following,"walk completed at 99")
  5.times {walk_step_fixture}
  check(o.flags[:walk_steps]==99,"indoor steps count")
  o.travel_coast(8,18);walk_step_fixture
  check(o.flags[:walk_steps]==100,"100th step missing")
  roundtrip
  o.travel(101,10,12); o.home_arrival
  check(o.flags[:walk_state]==:complete && !Followers.get(o::POOKIE_FOLLOWER),"home completion/follower cleanup")
end

o=Tidebound::Opening
[:NATU,:MAKUHITA,:POOCHYENA].each_with_index do |species,index|
  new_opening
  check($game_map.events[1].erased,"autorun")
  check($player.party.empty?,"early party")
  ids=o.household_pets.values.map { |p| Tidebound.identity(p) }
  o.begin_story
  check(ids.uniq.size==3 && o.household_pets.values.map { |p| Tidebound.identity(p) }==ids,"pet identity reroll")
  o.house_pet(species); check($player.party.empty?,"early choice")
  o.forest_gate; check($game_map.map_id!=103,"early forest")
  walk(index==1)
  check(!!o.flags[:walk_pier_seen] == (index==1),"pier was mandatory/repeated")
  check(!o.flags[:lamp_lit] && !o.flags[:oil_requested],"oil precedes choice")
  $choices=[false];o.house_pet(species);check($player.party.empty?,"cancel chose pet")
  chosen=o.household_pets[species]; id=Tidebound.identity(chosen)
  $player.name="Test Ren"; $choices=[true];o.house_pet(species)
  check($player.party==[chosen] && chosen.owner.name=="Test Ren" && Tidebound.identity(chosen)==id,"wrong individual")
  check(o.household_pets.size==2 && $bag.quantity(:POKEBALL)==8 && o.flags[:oil_requested],"selection supplies/oil")
  o::HOUSE_PETS.each_key { |s| o.house_pet(s) }
  check($player.party.size==1 && $bag.quantity(:POKEBALL)==8,"duplicate starter/supplies")
  o.travel_coast(21,12);o.shop_door;check($game_map.map_id==102,"shop unlocked early")
  o.outside_seller;check(o.flags[:keys_requested],"keys quest absent")
  o.oil_seller;check(!o.flags[:oil_collected],"oil outside")
  o.forest_gate; check($game_map.map_id==103,"forest requires lamp")
  o.forest_keys;o.forest_keys
  check($bag.quantity(:TIDEBOUNDOILKEYS)==1,"missing/duplicate keys")
  check(GameData::Item.get(:TIDEBOUNDOILKEYS).is_key_item?,"not a Key Item")
  roundtrip;check($bag.has?(:TIDEBOUNDOILKEYS),"keys not saved")
  o.travel_coast(21,12);o.outside_seller
  check(o.flags[:shop_unlocked] && !$bag.has?(:TIDEBOUNDOILKEYS),"unlock exchange")
  o.outside_seller;check(!o.flags[:oil_collected],"oil without entering")
  o.shop_door;check($game_map.map_id==106,"shop didn't open")
  o.oil_seller;o.travel(101,10,12);o.mother;o.main_lamp
  check(o.flags[:lamp_lit],"oil/lamp continuation")
  puts "PASS: #{species}; #{index==1 ? 'optional pier' : 'no pier'}; 99/100 steps, return, identity, keys/save/unlock/oil."
end

# 0.2 and 0.3 migrations, including an empty party after death.
[nil,3].each do |revision|
  [false,true].each do |chosen|
    new_opening
    old_pet=o.household_pets[:NATU]
    $player.party << old_pet if chosen || revision.nil?
    o.household_pets.delete(:NATU) if chosen
    o.flags[:opening_revision]=revision
    o.flags[:starter_chosen]=:NATU if chosen
    o.flags[:oil_collected]=true
    o.migrate_opening!
    check(o.flags[:walk_state]==:complete && o.flags[:shop_unlocked] && o.flags[:oil_collected],"migration progress")
    if chosen || revision.nil?
      check($player.party==[old_pet],"legacy companion changed")
    else
      $choices=[true];o.house_pet(:POOCHYENA)
      check($player.party.size==1,"old empty party cannot choose")
    end
    Tidebound.state.enter_astral!($player.party,{:map_id=>103});$player.party.clear
    o.flags[:opening_revision]=revision;o.migrate_opening!
    check($player.party.empty? && Tidebound.state.waiting_ids.size==1,"loss reset")
  end
end
puts "PASS: 0.2/0.3 migration, preserved oil, existing/unselected companions and astral losses."

new_opening;walk
$choices=[true];o.house_pet(:MAKUHITA)
o.forest_gate;$choices=[0];o.fire
check(Tidebound.state.checkpoint==[103,11,22,8],"checkpoint")
Tidebound.state.enter_astral!($player.party,{:map_id=>103});$player.party.clear;$game_map.map_id=105
o.astral_arrival;o.astral_arrival
check($player.party.size==1 && Tidebound.borrowed?($player.party.first),"guide duplication")
roundtrip
check(Tidebound.state.waiting_ids.size==1,"saved soul")
$choices=[true];o.return_from_astral
check($game_map.map_id==103 && Tidebound.state.memorials.size==1,"return/loss")
o.house_pet(:POOCHYENA);check($player.party.size==1,"replacement starter after death")
puts "PASS: chosen Makuhita loss, rest, guide, real SaveData and no replacement starter."
