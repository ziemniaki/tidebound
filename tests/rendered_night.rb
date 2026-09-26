# TEST ONLY: disposable native engine copy; no player saves. Uses a retained 0.3 save.
module TideboundNightInput
  def trigger?(key)
    return Graphics.frame_count%6==0 if key==Input::USE
    super
  end
end
Input.singleton_class.prepend(TideboundNightInput)
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('chosen-party.rxdata'))
  end
end
module TideboundNightView
  def night_shot(name)
    10.times { Graphics.update; updateSpritesets }
    b=Graphics.snap_to_bitmap;b.to_file("night-#{name}.png");b.dispose
  end
  def update
    super
    return if @night_checked || !$player || !$game_map
    return if pbMapInterpreterRunning? || $game_temp.message_window_showing
    @night_checked=true
    o=Tidebound::Opening
    raise 'old save lost companion' unless $player.party.first.species==:MAKUHITA
    raise 'clock shading enabled' if Settings::TIME_SHADING
    [0,6,12,18,23].each do |hour|
      t=Time.local(2026,9,10,hour)
      raise 'daylight leak' unless PBDayNight.isNight?(t) && !PBDayNight.isDay?(t) && !PBDayNight.isMorning?(t) && !PBDayNight.isAfternoon?(t) && !PBDayNight.isEvening?(t) && PBDayNight.getShade==0
    end
    o.travel_coast(5,11);night_shot('lighthouse')
    raise 'coast not night' unless $game_screen.tone.red==-80
    o.travel_coast(28,22);night_shot('beach')
    o.travel_coast(53,20);night_shot('pier')
    o.travel(103,17,25);night_shot('forest')
    raise 'forest not night' unless $game_screen.tone.red==-80
    o.travel(101,10,12);night_shot('home')
    raise 'interior lost lamplight' unless $game_screen.tone.red==-8
    o.travel(105,15,21)
    raise 'astral changed' unless $game_screen.tone.red==-55 && $game_screen.tone.gray==160
    o.travel(103,17,25)
    $tb_night_capture_battle=true
    WildBattle.start_core(:NATU,4)
  rescue Exception => e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('NIGHT_FAIL.txt',e.full_message);exit(1)
  end
end
Scene_Map.prepend(TideboundNightView)
module TideboundNightBattleView
  def pbStartBattle(*args)
    super
    return unless $tb_night_capture_battle
    raise 'day battle' unless @battle.time==2
    6.times { Graphics.update; pbUpdate }
    b=Graphics.snap_to_bitmap;b.to_file('night-battle.png');b.dispose
    File.write('NIGHT_PASS.txt',"PASS: retained 0.3 save; all clock hours resolve to night; coast/forest/interior/astral lighting; actual wild battle uses night and renders.\n")
    exit
  end
end
Battle::Scene.prepend(TideboundNightBattleView)
