# TEST ONLY. Loads a retained old save into a disposable engine directory.
module FieldInput
  def trigger?(key)
    return Graphics.frame_count%6==0 if key==Input::USE
    super
  end
end
Input.singleton_class.prepend(FieldInput)
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('vault-progress.rxdata'))
  end
end
module FieldView
  def shot(name)
    12.times { Graphics.update; updateSpritesets }
    b=Graphics.snap_to_bitmap;b.to_file("vault-#{name}.png");b.dispose
  end
  def update
    super
    return if @fields_checked || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @fields_checked=true
    o=Tidebound::Opening;v=Tidebound::VaultVisit
    raise 'saved vault visit' unless v.q[:gift] && v.q[:open] && v.q[:talk] && $bag.quantity(v::GIFT)==1
    raise 'saved NPCs' unless o.actor('Mother at vault').opacity==255 && o.actor('Seller at vault').opacity==255
    o.travel(110,17,6);shot('iron-door')
    v.q[:talk]=false;v.vault_door
    10.times { update;Graphics.update };shot('vault-conversation')
    raise 'walk up' unless $game_player.y==10 && v.q[:talk]
    o.travel(112,32,23);shot('museum-front')
    File.write('VAULT_RESUME_PASS.txt','PASS: actual engine save reload, keepsake and actor state; revised walk-up dialogue and museum doorway.')
    exit
  rescue Exception=>e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('VAULT_FAIL.txt',e.full_message);exit(1)
  end
end
Scene_Map.prepend(FieldView)
