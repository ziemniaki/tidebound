# Native Essentials objects/save codec; battle outcomes and scene services mocked.
class TrainerBattle
  def self.start_core(foe)
    raise 'not NPC trainer' unless foe.is_a?(NPCTrainer) && !foe.party.empty?
    if [2,5].include?($quest_outcome)
      $player.party.each { |p|p.hp=0 }
      Tidebound.before_cleanup_party=Tidebound.copy($player.party)
      $player.party.each(&:heal)
    end
    $quest_outcome
  end
end
def setBattleRule(*rules);$quest_rules=rules;end
n=Tidebound::NeighborQuest;o=Tidebound::Opening
[:NATU,:MAKUHITA,:POOCHYENA].each do |species|
  new_opening;walk;$choices=[true];o.house_pet(species)
  o.flags[:shop_unlocked]=true;o.travel(106,8,10);o.oil_seller;o.oil_seller
  check(n.stage==:pie && $bag.quantity(n::PIE)==1,'pie absent/duplicated')
  [n::PIE,n::PLATE,n::NECKLACE].each do |i|
    d=GameData::Item.get(i);check(d.is_key_item? && d.field_use==0 && d.battle_use==0,'healing/key item')
  end
  roundtrip;o.travel(101,10,12);o.mother
  check(o.flags[:oil_returned] && n.stage==:plate && $bag.has?(n::PLATE) && !$bag.has?(n::PIE),'meal')
  o.mother;check($bag.quantity(n::PLATE)==1,'repeat meal');o.main_lamp;roundtrip
  o.travel_coast(21,12);o.shop_door
  check(n.stage==:pursuit && !$bag.has?(n::PLATE),'robbery')
  n.robbery;roundtrip;n.south_gate;check($game_map.map_id==108,'south door')
  $quest_outcome=2;n.first_thief
  check(Tidebound.state.realm==:astral && $player.party.empty? && !n.q[:first_won],'loss advances')
  check(Tidebound.state.souls.last.pokemon.hp==0,'snapshot after heal')
  check($quest_rules.include?('canLose') && $quest_rules.include?('noMoney'),'rules');roundtrip
  point=Tidebound.return_to_living!;o.travel(*point);o.travel(108,26,23)
  $quest_outcome=1;n.first_thief;check(n.q[:first_won],'first win');roundtrip
  n.witness_hideout;n.hideout_door;n.overhear;check(n.q[:heard] && $game_map.map_id==109,'hideout')
  n.second_thief;check(!n.q[:second_won],'skipped runner')
  $quest_outcome=5;n.runner;check(!n.q[:runner_won] && n.stage==:pursuit,'draw advances')
  point=Tidebound.return_to_living!;o.travel(*point);o.travel(109,11,14)
  $quest_outcome=1;n.runner;n.second_thief
  check(n.stage==:necklace && $bag.quantity(n::NECKLACE)==1,'recovery')
  n.second_thief;roundtrip;o.travel(106,8,10);o.oil_seller
  check(n.stage==:complete && !$bag.has?(n::NECKLACE),'return')
  o.oil_seller;roundtrip
  check([n::PIE,n::PLATE,n::NECKLACE].none? { |i|$bag.has?(i) },'duplicated rewards')
  check(o.flags[:lamp_lit] && o.household_pets.size==2,'old progress reset')
  puts "PASS: #{species} whole quest; saved stages; trainer loss/draw/retry; unique items; preserved household."
end
new_opening;o.flags.merge!({:opening_revision=>4,:coast_revision=>5,:starter_chosen=>:MAKUHITA,:walk_state=>:complete,:hall_talk=>true,:oil_requested=>true,:oil_collected=>true,:oil_returned=>true,:lamp_lit=>true,:shop_unlocked=>true})
o.travel(106,8,10);o.oil_seller;check(n.stage==:pie && o.flags[:lamp_lit] && o.flags[:coast_revision]==5,'old oil save')
class PokemonBag
  alias quest_original_add add
  def add(item,*args);return false if item==$quest_reject_item;quest_original_add(item,*args);end
end
o.travel(101,10,12);$quest_reject_item=n::PLATE;n.meal
check(n.stage==:pie && $bag.has?(n::PIE),'full bag consumes pie')
$quest_reject_item=nil;n.meal;n.q.merge!({:stage=>:pursuit,:runner_won=>true,:second_won=>true})
$quest_reject_item=n::NECKLACE;n.second_thief;check(n.stage==:pursuit && n.q[:second_won],'earned item lost')
$quest_reject_item=nil;n.second_thief;check(n.stage==:necklace && $bag.quantity(n::NECKLACE)==1,'item retry')
puts 'PASS: completed-oil legacy save, full-bag meal rollback and necklace retry without rebattle.'
