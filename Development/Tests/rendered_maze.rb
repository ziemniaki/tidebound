# TEST ONLY. Inject into a disposable engine directory.
module MazeInput
 def trigger?(key)
  return !!($game_temp && $game_temp.message_window_showing && Graphics.frame_count%5==0) if key==Input::USE
  super
 end
end
Input.singleton_class.prepend(MazeInput)
class Scene_TideboundTitle
 def main
  SaveData.mark_values_as_unloaded
  file={'resume'=>'maze-mid.rxdata','legacy'=>'chosen-party.rxdata','complete'=>'maze-complete.rxdata'}[ENV['TB_MAZE_MODE']]
  file ? Game.load(SaveData.get_data_from_file(file)) : Game.start_new
 end
end
module MazeCheck
 def shot(name)
  160.times {Graphics.update;Input.update;update}
  b=Graphics.snap_to_bitmap;b.to_file("maze-#{name}.png");b.dispose
 end
 def step(d,n=1)
  n.times do
   8.times {Graphics.update;Input.update;update}
   old=[$game_map.map_id,$game_player.x,$game_player.y]
   $game_player.public_send("move_#{d}")
   28.times {Graphics.update;Input.update;update}
   raise "blocked #{d} #{old}" if old==[$game_map.map_id,$game_player.x,$game_player.y]
  end
 end
 def at(x,y);[$game_player.x,$game_player.y]==[x,y];end
 def update
  super
  return if @maze_test || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
  return unless Tidebound::Opening.flags[:opening_started]
  @maze_test=true;o=Tidebound::Opening;m=Tidebound::PsychicMaze;mode=ENV['TB_MAZE_MODE'] || 'new'
  if ['legacy','complete'].include?(mode)
   raise 'old save enters maze' if $game_map.map_id==114 || m.active?
   party=$player.party.map { |p| Tidebound.identity(p) };candies=$bag.quantity(:RARECANDY)
   o.travel(107,6,8);20.times {Graphics.update;Input.update;update};o.begin_story
   raise 'bedroom/initialization' unless $game_map.map_id==107 && !m.active? && $bag.quantity(:RARECANDY)==candies
   raise 'party changed' unless $player.party.map { |p| Tidebound.identity(p) }==party
   File.write("MAZE_#{mode}_PASS.txt",'PASS: saved journey retains normal bedroom, state, inventory and companion identities.');exit
  end
  raise 'initial setup' unless $game_map.map_id==114 && m.active? && $player.party.empty? && $bag.quantity(:RARECANDY)==99
  if mode=='resume'
   raise 'resume coordinates' unless at(17,11)
   saved=SaveData.get_data_from_file('maze-mid.rxdata')[:tidebound].story[:household_pets][:NATU]
   raise 'resume identity' unless Tidebound.identity(saved)==Tidebound.identity(o.household_pets[:NATU])
   step('left');step('right');raise 'resume input' unless at(17,11) && m.active?
   raise 'resave' unless Game.save('maze-resumed.rxdata')
   File.write('MAZE_resume_PASS.txt','PASS: native reload inside maze retains active state, position, Natu identity and 99 candies; movement and saving work.');exit
  end
  id=Tidebound.identity(o.household_pets[:NATU]);speed=$game_player.move_speed
  if mode=='new'
   raise 'start' unless at(5,20)
   shot('start');step('right',2);raise 'first slide' unless at(7,16)
   step('right',2);raise 'warp' unless at(4,11)
   step('right',3);raise 'wrong pad' unless at(5,20)
   step('right',2);step('right',2);step('up');raise 'return pad' unless at(9,17)
   step('up');raise 'pad bounce' unless at(4,11)
   step('left');step('up',2);raise 'long slide' unless at(17,11) && $game_player.move_speed==speed
   raise 'save' unless Game.save('maze-mid.rxdata')
  else
   raise 'resume' unless at(17,11)
  end
  step('left',6);step('up',4);shot('pushers');step('up',2);step('right',6);raise 'last slide' unless at(17,3)
  step('left');raise 'goal warp' unless at(22,5)
  step('down');raise 'return from goal' unless at(16,4)
  step('up');step('right');shot('natu');o.actor('Room:NATU').start
  30.times {Graphics.update;Input.update;update}
  raise 'completion' unless $game_map.map_id==107 && o.flags[:psychic_maze]==:complete && o.flags[:bedroom_talk]
  raise 'identity/party' unless Tidebound.identity(o.household_pets[:NATU])==id && $player.party.empty?
  shot('normal-room');$game_player.moveto(8,11);step('down')
  raise 'hall' unless $game_map.map_id==101 && o.flags[:hall_talk] && o.flags[:walk_state]==:requested
  raise 'candies repeated' unless $bag.quantity(:RARECANDY)==99
  o.travel(101,6,4);step('up');raise 'reentry' unless $game_map.map_id==107 && !m.active?
  raise 'save complete' unless Game.save('maze-complete.rxdata')
  File.write("MAZE_#{mode}_PASS.txt",'PASS: native new/resumed game; all slides and teleporters; wrong/return pads; Natu identity; Mother call; normal bedroom; hall/Pookie continuation; no duplicate supplies; save.');exit
 rescue Exception=>e
  raise if e.is_a?(SystemExit) && e.status==0
  File.write('MAZE_FAIL.txt',e.full_message);exit(1)
 end
end
Scene_Map.prepend(MazeCheck)
