# TEST ONLY. Native messages/movement/battles/save objects; automated input.
# Between-battle HP resets below isolate staging from difficulty/balance.
$stdout.sync=true
module QuestInput
  def trigger?(key)
    return Graphics.frame_count%6==0 if key==Input::USE
    super
  end
end
Input.singleton_class.prepend(QuestInput)
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    name=ENV['TB_NEIGHBOR_RESUME']
    Game.load(SaveData.get_data_from_file(name ? "quest-#{name}.rxdata" : 'chosen-party.rxdata'))
  end
end
module QuestBattleView
  def pbStartBattle(*args)
    super
    raise 'daytime battle' unless @battle.time==2
    5.times { Graphics.update;pbUpdate }
    b=Graphics.snap_to_bitmap;b.to_file("battle-#{$tb_battle_label}.png");b.dispose
  end
  def pbFightMenu(idx,*args,&block)
    preferred=@battle.battlers[idx].moves.index { |m| m.id==:ARMTHRUST && m.pp>0 }
    @lastMove[idx]=preferred if preferred
    super
  end
end
Battle::Scene.prepend(QuestBattleView)
EventHandlers.add(:on_frame_update,:quest_props_test,proc {
  n=Tidebound::NeighborQuest
  if n.meal_visible && !$tb_meal_shot
    b=Graphics.snap_to_bitmap;b.to_file('quest-meal.png');b.dispose;$tb_meal_shot=true
  end
  if n.pearl_visible && n.pearl_glint.to_f>0.8 && !$tb_pearl_shot
    b=Graphics.snap_to_bitmap;b.to_file('quest-pearl.png');b.dispose;$tb_pearl_shot=true
  end
})
module QuestNativeCheck
  def quest_shot(name)
    5.times { Graphics.update;updateSpritesets }
    b=Graphics.snap_to_bitmap;b.to_file("quest-#{name}.png");b.dispose
    File.write('NATIVE_PROGRESS.txt',name)
  end
  def quest_step(direction)
    old=[$game_player.x,$game_player.y];$game_player.public_send("move_#{direction}")
    25.times { Graphics.update;Input.update;update }
    raise "blocked #{direction}: #{old}" if old==[$game_player.x,$game_player.y]
  end
  def quest_save(name);raise 'save failed' unless Game.save("quest-#{name}.rxdata");end
  def update
    super
    return if @quest_checked || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @quest_checked=true;o=Tidebound::Opening;n=Tidebound::NeighborQuest
    if ENV['TB_NEIGHBOR_RESUME']
      name=ENV['TB_NEIGHBOR_RESUME'];raise 'stage not preserved' unless n.stage==name.to_sym
      raise 'coast migration' unless o.flags[:coast_revision]==5
      if name=='pursuit'
        o.travel(108,26,27);raise 'beaten thief reappeared' unless o.actor('Road thief').opacity==0 && o.actor('Road thief').through
      elsif name=='plate'
        raise 'plate missing' unless $bag.has?(n::PLATE)
        o.travel_coast(21,12);raise 'robbers leaked' unless o.actor('Robbery youth one').opacity==0
      end
      quest_shot("resume-#{name}");File.write("RESUME_#{name}_PASS.txt","PASS: complete native save, quest stage, actor visibility and coast revision.\n");exit
    end
    raise 'old companion lost' unless $player.party.first.species==:MAKUHITA
    original_id=Tidebound.identity($player.party.first)
    File.write('NATIVE_PARTY.txt',$player.party.map { |p| [p.name,p.level,p.hp,p.moves.map(&:id)] }.inspect)
    o.travel(106,8,7);o.oil_seller
    raise 'legacy pie' unless n.stage==:pie && $bag.has?(n::PIE)
    quest_shot('pie');quest_save('pie')
    o.travel(101,12,8);o.mother
    raise 'meal' unless n.stage==:plate && $tb_meal_shot && $bag.has?(n::PLATE)
    quest_shot('after-meal');quest_save('plate')
    o.travel_coast(21,12);o.shop_door
    raise 'robbery' unless n.stage==:pursuit && !$bag.has?(n::PLATE)
    quest_shot('robbery-end')
    o.travel_coast(30,30);quest_step('down');raise 'south door' unless $game_map.map_id==108
    raise 'road daylight' unless $game_screen.tone.red==-80 && PBDayNight.isNight?
    o.travel(108,20,11);quest_shot('road-wilds')
    $player.party.each(&:heal);$tb_battle_label='wild';n.wild(:shoreforager)
    raise "wild did not resolve: realm=#{Tidebound.state.realm}; outcome=#{$game_variables[1]}" unless n.q[:shoreforager_gone]
    $player.party.each(&:heal);o.travel(108,26,23);$tb_battle_label='first';quest_step('down')
    raise 'thief victory' unless n.q[:first_won] && Tidebound.state.realm==:living
    quest_shot('first-won');quest_save('pursuit')
    o.travel(108,28,43);quest_step('right');raise 'witness' unless n.q[:hideout_seen]
    o.travel(108,35,42);quest_step('up');raise 'hideout' unless $game_map.map_id==109 && n.q[:heard]
    quest_shot('hideout')
    $player.party.each(&:heal);$tb_battle_label='runner';n.runner;raise 'runner' unless n.q[:runner_won]
    $player.party.each(&:heal);$tb_battle_label='second';n.second_thief
    raise 'necklace' unless n.stage==:necklace && $bag.has?(n::NECKLACE)
    quest_save('necklace');o.travel(106,7,6);o.oil_seller
    raise 'return/glint' unless n.stage==:complete && !$bag.has?(n::NECKLACE) && $tb_pearl_shot
    raise 'identity replaced' unless Tidebound.identity($player.party.first)==original_id
    quest_shot('complete');quest_save('complete')
    o.travel(108,26,27)
    $player.party.each { |p|p.hp=1;p.moves.clear;p.learn_move(:SPLASH) };$tb_battle_label='loss'
    result=n.battle(:second)
    raise 'native loss not astral' unless result==:astral && Tidebound.state.realm==:astral && $game_map.map_id==105
    soul=Tidebound.state.souls.find { |r|r.id==original_id }
    raise 'postheal snapshot' unless soul && soul.pokemon.hp==0
    raise 'quest reset' unless n.stage==:complete
    quest_shot('trainer-loss')
    File.write('NEIGHBOR_PASS.txt',"PASS: old 0.3 native save; pie/meal/robbery; south transfer/wild; three trainer wins; movement triggers/overheard dialogue; necklace return/glint; same companion identity; native trainer loss reaches astral before autoheal. Test input and HP resets isolate staging, not balance.\n");exit
  rescue Exception=>e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('NEIGHBOR_FAIL.txt',e.full_message);puts e.full_message;exit(1)
  end
end
Scene_Map.prepend(QuestNativeCheck)
