# TEST ONLY: inject with folded_path.rb into a disposable engine.
$tb_choices=[];$tb_seen={};$tb_hold=0
module FoldedTestInput
 def trigger?(key)
  return false if $tb_hold.to_i>0 && [Input::USE,Input::BACK].include?(key)
  return true if key==Input::USE && ($tb_reading || ($game_temp && $game_temp.message_window_showing)) && Graphics.frame_count%4==0
  super
 end
end
Input.singleton_class.prepend(FoldedTestInput)
module FoldedTestFrames
 def update
  super
  if $tb_hold.to_i>0
   $tb_hold-=1
   if $tb_hold==1 && $tb_capture
    b=Graphics.snap_to_bitmap;b.to_file("folded-#{$tb_capture}.png");b.dispose;$tb_capture=nil
   end
  end
 end
end
Graphics.singleton_class.prepend(FoldedTestFrames)
alias folded_original_message pbMessage
def pbMessage(message,commands=nil,cmdIfCancel=0,skin=nil,defaultCmd=0,&block)
 File.open('progress.txt','a') { |f|f.puts(message) }
 if commands
  raise "No test choice: #{message}" if $tb_choices.empty?
  choice=$tb_choices.shift
  return -1 if choice==-1
  defaultCmd=choice
  if message=='How long would you like to sleep?' || message=='Which tooth keeps the house standing?'
   expected=$game_map.map_id==115 ? [3,5] : [24,5]
   raise 'decision off bed' unless [$game_player.x,$game_player.y]==expected
   unless $tb_seen[message]
    $tb_seen[message]=true;$tb_capture=$game_map.map_id==115 ? 'sleep-menu' : 'four-questions';$tb_hold=70
   end
  end
 end
 folded_original_message(message,commands,cmdIfCancel,skin,defaultCmd,&block)
end
module CurseCapture
 def water_curse
  $tb_capture='water-curse';$tb_hold=70
  super
 end
end
Tidebound::DreamRoom.singleton_class.prepend(CurseCapture)
class Scene_TideboundTitle
 def main
  SaveData.mark_values_as_unloaded
  file={'resume'=>'folded-mid.rxdata','legacy'=>'chosen-party.rxdata','complete'=>'folded-complete.rxdata','oldroom'=>'old-room.rxdata'}[ENV['TB_FOLDED_MODE']]
  file ? Game.load(SaveData.get_data_from_file(file)) : Game.start_new
  $PokemonSystem.textspeed=3
 end
end
module FoldedCheck
 def frames(n=25);n.times {Graphics.update;Input.update;update};end
 def shot(name)
  frames(40);b=Graphics.snap_to_bitmap;b.to_file("folded-#{name}.png");b.dispose
 end
 def step(d,n=1)
  n.times do
   frames(5);old=[$game_map.map_id,$game_player.x,$game_player.y]
   $game_player.public_send("move_#{d}");frames(25)
   raise "blocked #{d} #{old}" if old==[$game_map.map_id,$game_player.x,$game_player.y]
  end
 end
 def at(x,y);[$game_player.x,$game_player.y]==[x,y];end
 def update
  super
  return if @folded_test || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
  return unless Tidebound::Opening.flags[:opening_started]
  @folded_test=true;o=Tidebound::Opening;d=Tidebound::DreamRoom;m=Tidebound::PsychicMaze
  mode=ENV['TB_FOLDED_MODE'] || 'new'
  if ['legacy','complete'].include?(mode)
   ids=$player.party.map { |p|Tidebound.identity(p) };candies=$bag.quantity(:RARECANDY)
   raise 'old save active' if d.active?
   o.travel(115,7,8);frames;raise 'reopened first room' unless $game_map.map_id==107
   o.travel(116,7,22);frames;raise 'reopened second room' unless $game_map.map_id==107
   raise 'old save reset' unless $bag.quantity(:RARECANDY)==candies && ids==$player.party.map { |p|Tidebound.identity(p) }
  else
   id=Tidebound.identity(o.household_pets[:NATU])
   raise 'party/supplies' unless $player.party.empty? && $bag.quantity(:RARECANDY)==99
   if mode=='new' || mode=='oldroom'
    raise 'new start' unless $game_map.map_id==115 && d.active?
    raise 'old PC cached' if $game_map.events.values.any? { |e|e.name=='Dream computer' }
    shot('small-room');[7,8].each do |x|
     $game_player.moveto(x,11);step('down');raise 'loop' unless at(7,8) && $game_player.opacity==255
    end
    $tb_choices=[0,1,2,3];d.cupboard
    $tb_reading=true
    $tb_choices=[1,0];d.inspect_object(:shelf);$tb_reading=false
    raise 'curse mutated puzzle' unless d.q[:water_curse_read] && d.q[:phase]==(mode=='oldroom' ? :wick : :sealed)
    if mode=='new'
     $tb_choices=[1,2,1];d.bed;raise 'wrong run' unless d.q[:streak]==0 && at(4,7)
     $tb_choices=[1,2,0,0];d.bed;raise 'short sleep' unless d.q[:phase]==:sealed && at(4,7)
     $tb_choices=[-1];d.bed;raise 'cancel bed' unless at(4,7)
     $tb_choices=[6];d.bed;frames
     raise 'wick' unless d.wick_visible? && !o.actor('Room:NATU').through
    end
    o.actor('Room:NATU').start;frames(40)
    raise 'second arrival' unless $game_map.map_id==116 && d.q[:phase]==:folded && at(7,22)
    shot('second-start')
    if mode=='oldroom'
     $game_player.moveto(25,7)
    else
     FOLDED_TEST_PATH.each { |direction|step(direction) }
    end
    raise 'route to bed' unless at(25,7)
    raise 'save second' unless Game.save('folded-mid.rxdata')
   else
    raise 'resume second' unless $game_map.map_id==116 && d.q[:phase]==:folded && at(25,7)
   end
   d::FOLDED_TEXT.keys.each { |key|d.folded_reading(key) } if mode=='new'
   answers=[1,0,2,1]
   if mode=='new'
    4.times do |i|
     $game_player.moveto(25,7);$tb_choices=answers.take(i)+[(answers[i]+1)%3];d.folded_bed
     raise "wrong #{i}" unless at(7,22) && d.q[:folded_streak]==0 && d.q[:phase]==:folded && $game_player.opacity==255
    end
    $game_player.moveto(25,7);$tb_choices=[-1];d.folded_bed
    raise 'cancel four' unless at(7,22) && d.q[:folded_streak]==0
   end
   $game_player.moveto(25,7);$tb_choices=answers.dup;d.folded_bed;frames
   raise 'maze arrival' unless $game_map.map_id==114 && at(5,20) && d.q[:phase]==:complete && m.active?
   raise 'Natu identity' unless id==Tidebound.identity(o.household_pets[:NATU])
   if mode=='new'
    step('right',2);step('right',2);step('left');step('up',2)
    step('left',6);step('up',6);step('right',6);step('left');step('right')
    o.actor('Room:NATU').start;frames(40)
    raise 'normal bedroom' unless $game_map.map_id==107 && !m.active? && o.flags[:bedroom_talk]
    $game_player.moveto(8,11);step('down')
    raise 'hall' unless $game_map.map_id==101 && o.flags[:hall_talk] && o.flags[:walk_state]==:requested
    raise 'save complete' unless Game.save('folded-complete.rxdata')
   end
  end
  raise 'unconsumed choices' unless $tb_choices.empty?
  File.write("FOLDED_#{mode}_PASS.txt","PASS #{mode}: room state, physical bed staging, rendered effects, native choices, reset/route/continuation, identity and inventory.");exit
 rescue Exception=>e
  raise if e.is_a?(SystemExit) && e.status==0
  File.write('FOLDED_FAIL.txt',e.full_message);exit(1)
 end
end
Scene_Map.prepend(FoldedCheck)
