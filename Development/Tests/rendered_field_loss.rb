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
    Game.load(SaveData.get_data_from_file('chosen-party.rxdata'))
  end
end
module FieldView
  def shot(name)
    12.times { Graphics.update; updateSpritesets }
    b=Graphics.snap_to_bitmap;b.to_file("field-#{name}.png");b.dispose
  end
  def update
    super
    return if @fields_checked || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @fields_checked=true
    p=$player.party.first;id=Tidebound.identity(p)
    p.hp=1
    Tidebound::Opening.travel(108,30,18)
    outcome=WildBattle.start(:EKANS,100,can_override:true)
    raise 'did not lose' unless outcome==2 && Tidebound.state.realm==:astral && $game_map.map_id==105
    soul=Tidebound.state.souls.first
    raise 'identity/snapshot' unless soul.id==id && soul.pokemon.hp==0
    File.write('FIELD_LOSS_PASS.txt','PASS: native grass-entry battle defeat transfers to astral and preserves zero-HP original companion snapshot.')
    exit
  rescue Exception=>e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('FIELD_FAIL.txt',e.full_message);exit(1)
  end
end
Scene_Map.prepend(FieldView)
