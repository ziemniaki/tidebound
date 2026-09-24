# TEST ONLY. New Game must run the real scene and real movement/collision code.
$bird_test_direction=0
module BirdTestInput
 def dir4;return $bird_test_direction if $scene.is_a?(Scene_TideboundBirdPrelude);super;end
 def trigger?(key)
  return !!($game_temp && $game_temp.message_window_showing && Graphics.frame_count%4==0) if key==Input::USE
  super
 end
end
Input.singleton_class.prepend(BirdTestInput)
class Scene_TideboundTitle
 def main
  SaveData.mark_values_as_unloaded
  mode=ENV['TB_BIRD_MODE']
  mode=='continue' ? Game.load(SaveData.get_data_from_file('bird-room.rxdata')) : mode=='legacy' ? Game.load(SaveData.get_data_from_file('chosen-party.rxdata')) : Game.start_new
  $PokemonSystem.textspeed=3
 end
end
module BirdSceneCheck
 def test_shot(name)
  b=Graphics.snap_to_bitmap;b.to_file("bird-#{name}.png");b.dispose
 end
 def path(a,b)
  queue=[[a,[]]];seen={a=>true}
  until queue.empty?
   cell,route=queue.shift;return route if cell==b
   [[2,0,1],[4,-1,0],[6,1,0],[8,0,-1]].each do |d,dx,dy|
    p=[cell[0]+dx,cell[1]+dy];next unless Tidebound::BirdPrelude.passable?(p) && !seen[p]
    seen[p]=true;queue<<[p,route+[[d,p]]]
   end
  end
  raise 'no route'
 end
 def update
  super
  @checked_phases||={}
  if @phase==:sleep && @time>0.9 && !@checked_phases[:sleep]
   raise 'early initialization' if Tidebound::Opening.flags[:opening_started]
   test_shot('asleep');@checked_phases[:sleep]=true
  elsif @phase==:eye && @time>2.3 && !@checked_phases[:eye]
   test_shot('eye');@checked_phases[:eye]=true
  elsif @phase==:caption && @time>4.5 && !@checked_phases[:caption]
   test_shot('caption');@checked_phases[:caption]=true
  elsif @phase==:moving && @time-@game_started>1.4
   unless @checked_phases[:maze]
    test_shot('maze');@checked_phases[:maze]=true;@blocked_started=@time
   end
   # Start's left neighbor is void: held movement must not leave the path.
   if @time-@blocked_started<0.4
    $bird_test_direction=4;raise 'void traversed' unless @cell==Tidebound::BirdPrelude::START
    return
   end
   # Deliberately visit a blind branch, then return and reach the bedside.
   @test_route||=path(@cell,[1,6])+path([1,6],Tidebound::BirdPrelude::GOAL)
   @test_route.shift if !@test_route.empty? && @cell==@test_route.first[1]
   $bird_test_direction=@test_route.empty? ? 0 : @test_route.first[0]
  elsif @phase==:arrival && !@checked_phases[:arrival]
   test_shot('bedside');@checked_phases[:arrival]=true
   raise 'goal/room initialization' unless @cell==Tidebound::BirdPrelude::GOAL && !Tidebound::Opening.flags[:opening_started]
   File.write('BIRD_SCENE_PASS.txt','PASS: sleep/eye/caption, native input, void collision, dead-end return, bedside approach. No premature room initialization.')
  end
 end
end
Scene_TideboundBirdPrelude.prepend(BirdSceneCheck)
module BirdRoomCheck
 def update
  super
  return if @bird_checked || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
  return unless Tidebound::Opening.flags[:opening_started]
  @bird_checked=true;mode=ENV['TB_BIRD_MODE'] || 'new';o=Tidebound::Opening
  if mode=='legacy'
   raise 'replayed prelude' if o.flags[:bird_prelude_seen]
  else
   raise 'room transfer' unless $game_map.map_id==115 && o.flags[:bird_prelude_seen] && o.flags[:dream_room][:phase]==:sealed
   raise 'human/supplies/household' unless $bag.quantity(:RARECANDY)==99 && $player.party.empty? && o.household_pets.keys.sort==[:MAKUHITA,:NATU,:POOCHYENA].sort
   raise 'avatar invisible' unless $game_player.opacity==255
   if mode=='new'
    raise 'scene missing' unless File.exist?('BIRD_SCENE_PASS.txt')
    b=Graphics.snap_to_bitmap;b.to_file('bird-room.png');b.dispose
    raise 'save room' unless Game.save('bird-room.rxdata')
   end
  end
  File.write("BIRD_#{mode}_PASS.txt","PASS #{mode}: correct first-room handoff or Continue; normal human, one-time household and inventory initialization.");exit
 rescue Exception=>e
  raise if e.is_a?(SystemExit) && e.status==0
  File.write('BIRD_FAIL.txt',e.full_message);exit(1)
 end
end
Scene_Map.prepend(BirdRoomCheck)
