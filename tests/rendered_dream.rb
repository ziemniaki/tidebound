# TEST ONLY: disposable native engine, never distributed in the script archive.
$dream_choices=[]
module DreamInput
 def trigger?(key)
  return !!($game_temp && $game_temp.message_window_showing && Graphics.frame_count%5==0) if key==Input::USE
  super
 end
end
Input.singleton_class.prepend(DreamInput)
alias dream_original_message pbMessage
def pbMessage(message,commands=nil,cmdIfCancel=0,skin=nil,defaultCmd=0,&block)
 if commands && $dream_choices
  raise "No test choice for #{message}" if $dream_choices.empty?
  choice=$dream_choices.shift
  return -1 if choice==-1 # Logical cancellation; actual menus tested for all other choices.
  defaultCmd=choice
 end
 dream_original_message(message,commands,cmdIfCancel,skin,defaultCmd,&block)
end
class Scene_TideboundTitle
 def main
  SaveData.mark_values_as_unloaded
  file={'sealed'=>'dream-sealed.rxdata','wick'=>'dream-wick.rxdata','legacy'=>'chosen-party.rxdata','complete'=>'dream-complete.rxdata'}[ENV['TB_DREAM_MODE']]
  file ? Game.load(SaveData.get_data_from_file(file)) : Game.start_new
 end
end
module DreamCheck
 def frames(n=25);n.times {Graphics.update;Input.update;update};end
 def shot(name)
  frames(60);b=Graphics.snap_to_bitmap;b.to_file("dream-#{name}.png");b.dispose
 end
 def step(d,n=1)
  n.times do
   frames(8);old=[$game_map.map_id,$game_player.x,$game_player.y]
   $game_player.public_send("move_#{d}");frames(28)
   raise "blocked #{d} #{old}" if old==[$game_map.map_id,$game_player.x,$game_player.y]
  end
 end
 def at(x,y);[$game_player.x,$game_player.y]==[x,y];end
 def update
  super
  return if @dream_test || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
  return unless Tidebound::Opening.flags[:opening_started]
  @dream_test=true;o=Tidebound::Opening;d=Tidebound::DreamRoom;m=Tidebound::PsychicMaze
  mode=ENV['TB_DREAM_MODE'] || 'new'
  if ['legacy','complete'].include?(mode)
   raise 'old save entered dream' if d.active? || $game_map.map_id==115
   ids=$player.party.map { |p|Tidebound.identity(p) };candies=$bag.quantity(:RARECANDY)
   o.travel(107,6,8);frames;o.begin_story
   raise 'old save reset' unless !d.active? && $bag.quantity(:RARECANDY)==candies && ids==$player.party.map { |p|Tidebound.identity(p) }
   o.travel(115,7,8);frames
   raise 'dream reopened' unless $game_map.map_id==107
  else
   raise 'start initialization' unless $game_map.map_id==115 && d.active? && $player.party.empty? && $bag.quantity(:RARECANDY)==99
   id=Tidebound.identity(o.household_pets[:NATU])
   if mode=='new'
    raise 'Wick early' if d.wick_visible?
    shot('start')
    [7,8].each do |x|
     $game_player.moveto(x,11);step('down');raise 'exit loop' unless at(7,8) && $game_map.map_id==115
    end
    $dream_choices=[0,1,2,3];d.computer
    d::TEXT.keys.each { |key|d.inspect_object(key) }
    $dream_choices=[1,2,1];d.bed
    raise 'wrong answer did not reset' unless d.q[:streak]==0 && !d.q[:riddles_solved]
    $dream_choices=[-1];d.bed;raise 'cancel reset' unless d.q[:streak]==0
    $dream_choices=[1,2,0,7];d.bed
    raise 'three correct' unless d.q[:riddles_solved] && d.q[:streak]==3 && !d.wick_visible?
    $dream_choices=[-1];d.bed
    6.times do |i|
     $dream_choices=[i];d.bed
     raise 'short sleep advanced' unless d.q[:phase]==:sealed && d.q[:last_sleep]==d::DURATIONS[i] && $game_map.map_id==115
    end
    raise 'save sealed' unless Game.save('dream-sealed.rxdata')
   elsif mode=='sealed'
    raise 'sealed resume' unless d.q[:riddles_solved] && d.q[:phase]==:sealed && !d.wick_visible?
   end
   unless mode=='wick'
    $dream_choices=[6];d.bed;frames
    raise 'Wick appearance' unless d.wick_visible? && !o.actor('Room:NATU').through
    raise 'save wick' unless Game.save('dream-wick.rxdata')
   end
   raise 'wick load' unless d.wick_visible?
   shot('wick');$game_player.moveto(9,8);$game_player.turn_right;o.actor('Room:NATU').start;frames(40)
   raise 'maze transition' unless $game_map.map_id==114 && at(5,20) && m.active? && d.q[:phase]==:complete
   shot('maze')
   if mode=='wick'
    raise 'restored identity' unless id==Tidebound.identity(o.household_pets[:NATU])
    File.write('DREAM_wick_PASS.txt','PASS: reload after materialization retains visible Wick, inventory, identity and working maze transition.');exit
   end
   step('right',2);step('right',2);step('left');step('up',2)
   step('left',6);step('up',6);step('right',6);step('left');step('right')
   o.actor('Room:NATU').start;frames(40)
   raise 'normal bedroom' unless $game_map.map_id==107 && o.flags[:bedroom_talk] && !m.active?
   raise 'Natu changed' unless id==Tidebound.identity(o.household_pets[:NATU]) && $player.party.empty?
   shot('normal-room');$game_player.moveto(8,11);step('down')
   raise 'hall continuation' unless $game_map.map_id==101 && o.flags[:hall_talk] && o.flags[:walk_state]==:requested
   raise 'duplicated items' unless $bag.quantity(:RARECANDY)==99
   raise 'save complete' unless Game.save('dream-complete.rxdata')
  end
  File.write("DREAM_#{mode}_PASS.txt","PASS: #{mode}; false bedroom, state, native messages/menus, Wick/maze/normal-room continuity, inventory and household identity.");exit
 rescue Exception=>e
  raise if e.is_a?(SystemExit) && e.status==0
  File.write('DREAM_FAIL.txt',e.full_message);exit(1)
 end
end
Scene_Map.prepend(DreamCheck)
