# TEST ONLY. Actual native screenshots; positions selected for useful framing.
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('interior-progress.rxdata'))
  end
end
module InteriorViews
  def view_shot(name)
    200.times {Graphics.update;Input.update;update}
    b=Graphics.snap_to_bitmap;b.to_file("view-#{name}.png");b.dispose
  end
  def update
    super
    return if @views_done || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @views_done=true;o=Tidebound::Opening;v=Tidebound::VaultVisit
    o.flags[:walk_state]=:requested;o.travel(107,8,8);view_shot('bedroom')
    o.flags[:walk_state]=:complete;v.q[:museum]=true
    o.travel(101,10,8);view_shot('living-room')
    o.flags[:lamp_lit]=true;o.travel(104,6,6);view_shot('lantern')
    o.travel(110,13,8);view_shot('cellar')
    v.q[:museum]=false;v.q[:open]=true;v.q[:talk]=true
    o.travel(111,12,10);view_shot('vault')
    o.travel(111,12,15);view_shot('vault-aisle')
    File.write('VIEWS_PASS.txt','Six unmodified native engine captures.');exit
  rescue Exception=>e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('VIEWS_FAIL.txt',e.full_message);exit(1)
  end
end
Scene_Map.prepend(InteriorViews)
