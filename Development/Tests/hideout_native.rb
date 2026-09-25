# TEST ONLY. Inject into a disposable Linux engine, never the release Scripts.
$stdout.sync=true
module HideoutTestInput
  def trigger?(key)
    return Graphics.frame_count%6==0 if key==Input::USE
    return false if key==Input::BACK
    super
  end
  def dir4
    s=$mending_test_scene;return super unless s
    g=s.game;goal=Tidebound::Mending::NESTS.each_with_index.find { |_c,i| !g.freed.include?(i) }
    target=goal ? goal[0] : Tidebound::Mending::EXIT
    return 0 if g.cell==target
    time=s.instance_variable_get(:@time)
    hazard=[9,6+(Math.sin(time*0.75)>0 ? 0 : 1)]
    todo=[[g.cell,[]]];seen={g.cell=>true}
    until todo.empty?
      cell,path=todo.shift
      return path.first if cell==target
      {2=>[0,1],4=>[-1,0],6=>[1,0],8=>[0,-1]}.each do |d,delta|
        p=[cell[0]+delta[0],cell[1]+delta[1]]
        next unless Tidebound::Mending::CELLS[p] && p!=hazard && !seen[p]
        seen[p]=true;todo<<[p,path+[d]]
      end
    end
    0
  end
end
Input.singleton_class.prepend(HideoutTestInput)
module HideoutTestScene
  def main
    $mending_test_scene=self
    super
  ensure
    $mending_test_scene=nil
  end
  def update(dt)
    result=super
    if @time>5.2 && !@test_shot
      b=Graphics.snap_to_bitmap;b.to_file('hideout-mending.png');b.dispose;@test_shot=true
    end
    raise 'minigame timeout' if @time>90
    result
  end
end
Scene_TideboundMending.prepend(HideoutTestScene)
class Scene_TideboundTitle
  def main
    $data_system.start_map_id=109;$data_system.start_x=11;$data_system.start_y=14
    Game.start_new;$scene=Scene_Map.new
    $player.name='Ren'
    Tidebound::Opening.flags.merge!(opening_started:true,opening_revision:4,coast_revision:5,starter_chosen: :NATU)
    Tidebound::NeighborQuest.q.merge!(stage: :pursuit,first_won:true)
    hero=Pokemon.new(:NATU,45);hero.learn_move(:PSYCHIC);hero.moves=[Pokemon::Move.new(:PSYCHIC)]
    $player.party=[hero];$bag.add(:POKEBALL,5)
    Tidebound.state.checkpoint=[108,26,39,8]
    if ENV['TB_HIDEOUT_RENDER']=='1'
      scene=Scene_TideboundMending.new
      raise 'minigame incomplete' unless scene.main
      raise 'scene resource leak' unless scene.instance_variable_get(:@sprites).all?(&:disposed?) && scene.instance_variable_get(:@bitmaps).all?(&:disposed?)
      File.write('MENDING_NATIVE_PASS.txt','PASS: final artwork, full minigame controls and exit, all sprites and bitmaps disposed.');exit
    end
  end
end
module HideoutNativeCheck
  def shot(name)
    8.times { Graphics.update;Input.update;updateSpritesets }
    b=Graphics.snap_to_bitmap;b.to_file("hideout-#{name}.png");b.dispose
  end
  def update
    super
    return if @hideout_test || !$player || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @hideout_test=true
    h=Tidebound::Hideout;n=Tidebound::NeighborQuest
    if ENV['TB_HIDEOUT_ATMOSPHERE']=='1'
      $game_player.moveto(8,10);shot('squat-west')
      $game_player.moveto(16,5);shot('squat-sofa')
      File.write('ATMOSPHERE_NATIVE_PASS.txt','PASS: native map109 renders both clutter maze and sofa area.');exit
    end
    if ENV['TB_HIDEOUT_CACHE']=='1'
      n.q[:runner_won]=true;n.q[:second_won]=true
      h.actor.character_name='trainer_CAMPER'
      [[16,5],[15,5],[14,6],[15,7]].each do |pos|
        h.actor.moveto(16,4);$game_player.moveto(*pos)
        h.lead_to_cache;h.follow_to_cache
        raise 'player did not follow to cupboard' unless [$game_player.x,$game_player.y]==[13,5]
        raise 'actor collision leaked' if h.actor.through
      end
      h.handoff;shot('necklace')
      raise 'handoff' unless n.stage==:necklace && $bag.quantity(n::NECKLACE)==1
      File.write('CACHE_NATIVE_PASS.txt','PASS: actual NPC and player routes from all four approach tiles; collision restored; unique necklace.');exit
    end
    shot('entrance')
    # Actual movement into the guard trigger, then native TrainerBattle.
    $game_player.moveto(14,10);$game_player.move_up
    35.times { Graphics.update;Input.update;update }
    raise 'approach battle not won' unless n.q[:runner_won]
    $game_player.moveto(16,5);shot('sofa')
    h.boss
    raise 'minigame/boss not complete' unless n.q[:hideout_game_won] && n.q[:second_won] && n.stage==:necklace
    raise 'necklace missing' unless $bag.quantity(n::NECKLACE)==1
    raise 'actor did not lead' unless [h.actor.x,h.actor.y]==[13,4] && !h.actor.through
    raise 'player did not follow' unless [$game_player.x,$game_player.y]==[13,5]
    shot('necklace')
    h.boss;raise 'necklace duplicated' unless $bag.quantity(n::NECKLACE)==1
    raise 'save failed' unless Game.save('hideout-complete.rxdata')
    data=SaveData.get_data_from_file('hideout-complete.rxdata')
    raise 'saved flag missing' unless Marshal.dump(data).include?('hideout_game_won')
    File.write('HIDEOUT_NATIVE_PASS.txt','PASS: native map/sofa render; player-touch guard battle; full minigame via real controls; boss battle; animated cache route; one necklace; native save.');exit
  rescue Exception=>e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('HIDEOUT_NATIVE_FAIL.txt',e.full_message);puts e.full_message;exit(1)
  end
end
Scene_Map.prepend(HideoutNativeCheck)
