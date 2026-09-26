# TEST ONLY. Full native save loads in disposable game copy.
$tb_coast_resume=ENV.fetch('TB_COAST_RESUME','legacy-coast')
module TideboundCoastResumeInput
  def trigger?(key)
    return Graphics.frame_count%6==0 if key==Input::USE
    super
  end
end
Input.singleton_class.prepend(TideboundCoastResumeInput)
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file("#{$tb_coast_resume}.rxdata"))
  end
end
module TideboundCoastResume
  def update
    super
    return if @coast_resume || !$player || !$game_map
    return if pbMapInterpreterRunning? || $game_temp.message_window_showing
    @coast_resume=true
    o=Tidebound::Opening
    raise 'wrong map' unless $game_map.map_id==102
    raise 'migration flag' unless o.flags[:coast_revision]==5
    x,y=$game_player.x,$game_player.y
    raise 'water spawn' unless Tidebound::MAP_PASSAGES[102][y][x]=='1'
    raise 'distance lost' unless o.flags[:walk_steps]==100
    raise 'household lost' unless o.household_pets.size==3 && $player.party.empty?
    if $tb_coast_resume=='coast-pier'
      raise 'pier state' unless o.flags[:walk_state]==:at_pier
      dog=o.actor('Pookie outside')
      raise 'pier location' unless [dog.x,dog.y]==o.coast_xy(*o::POOKIE_PIER)
      raise 'duplicate follower' if Followers.get(o::POOKIE_FOLLOWER)
      o.pookie
    else
      raise 'follower lost' unless Followers.get(o::POOKIE_FOLLOWER)
      if $tb_coast_resume=='legacy-coast' || $tb_coast_resume=='coast-following' || $tb_coast_resume=='coast-current'
        raise "wrong translated position #{[x,y]}" unless [x,y]==o.coast_xy(9,17)
      end
      follower=Followers.get(o::POOKIE_FOLLOWER)
      raise 'follower outside region' unless follower.x.between?(24,79) && follower.y.between?(23,46)
    end
    o.migrate_coast!
    raise 'double translation' unless [$game_player.x,$game_player.y]==[x,y]
    raise 'current save' unless Game.save('coast-current.rxdata')
    File.write("RESUME_#{$tb_coast_resume}_PASS.txt","PASS: full native save load, safe coastal position, pet/quest/follower preservation, idempotent migration.\n")
    exit
  rescue Exception => e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write("RESUME_#{$tb_coast_resume}_FAIL.txt",e.full_message)
    exit(1)
  end
end
Scene_Map.prepend(TideboundCoastResume)
