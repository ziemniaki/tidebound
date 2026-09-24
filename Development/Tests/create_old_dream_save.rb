# Inject into the unmodified 0.7.18 archive in a disposable engine.
module OldDreamInput
 def trigger?(key)
  return !!($game_temp && $game_temp.message_window_showing && Graphics.frame_count%4==0) if key==Input::USE
  super
 end
end
Input.singleton_class.prepend(OldDreamInput)
class Scene_TideboundTitle
 def main;SaveData.mark_values_as_unloaded;Game.start_new;$PokemonSystem.textspeed=3;end
end
module OldDreamSave
 def update
  super
  return if @saved || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
  return unless Tidebound::Opening.flags[:opening_started]
  @saved=true
  raise 'not baseline computer' unless $game_map.events.values.any? { |e|e.name=='Dream computer' }
  Tidebound::DreamRoom.q[:phase]=:wick;Tidebound::DreamRoom.q[:riddles_solved]=true
  raise 'save' unless Game.save('old-room.rxdata')
  File.write('OLD_SAVE_PASS.txt','Genuine 0.7.18 map115/CRT save, phase wick, 99 candies, household identities.');exit
 end
end
Scene_Map.prepend(OldDreamSave)
