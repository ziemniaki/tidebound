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
    Tidebound.story[:walk_state]=:requested;Tidebound::World.travel(:bedroom,8,8);view_shot('bedroom')
    Tidebound.story[:walk_state]=:complete;v.q[:museum]=true
    Tidebound::World.travel(:home,10,8);view_shot('living-room')
    Tidebound.story[:lamp_lit]=true;Tidebound::World.travel(:lantern,6,6);view_shot('lantern')
    Tidebound::World.travel(:basement,13,8);view_shot('cellar')
    v.q[:museum]=false;v.q[:open]=true;v.q[:talk]=true
    Tidebound::World.travel(:vault,12,10);view_shot('vault')
    Tidebound::World.travel(:vault,12,15);view_shot('vault-aisle')
    File.write('VIEWS_PASS.txt','Six unmodified native engine captures.');exit
  rescue Exception=>e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('VIEWS_FAIL.txt',e.full_message);exit(1)
  end
end
Scene_Map.prepend(InteriorViews)
