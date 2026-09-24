# TEST ONLY: inject before Main in a disposable native runtime.
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('chosen-party.rxdata'))
  end
end
module LaprasTest
  def update
    super
    return if @lapras_checked || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @lapras_checked = true
    paths = Dir.glob('PBS/pokemon*.txt').reject { |s| s =~ /pokemon_(forms|metrics)/ }
    Compiler.compile_pokemon(*paths)
    Compiler.compile_pokemon_forms(*Dir.glob('PBS/pokemon_forms*.txt'))
    p = Pokemon.new(:LAPRAS_1, 10)
    raise 'regional constructor' unless p.species == :LAPRAS && p.form == 1 && p.types == [:WATER, :GHOST]
    stock = Pokemon.new(:LAPRAS, 10)
    raise 'ordinary Lapras' unless stock.form == 0 && stock.types == [:WATER, :ICE]
    [:base_stats, :moves, :abilities, :hidden_abilities, :evolutions].each do |field|
      raise "inherited #{field}" unless p.species_data.send(field) == stock.species_data.send(field)
    end
    id = Tidebound.state.assign_identity(p)
    copy = Marshal.load(Marshal.dump(p))
    raise 'saved form' unless copy.form == 1 && copy.types == [:WATER, :GHOST]
    souls = Tidebound::State.new
    copy.hp = 0
    souls.enter_astral!([copy], {map_id:102,x:77,y:40})
    raise 'astral form' unless souls.begin_encounter!(id).form == 1
    recovered = souls.recover!(id)
    raise 'recovery identity' unless recovered.form == 1 && Tidebound.identity(recovered) == id
    [false,true].each do |shiny|
      p.shiny = shiny
      [false,true].each do |back|
        b = GameData::Species.sprite_bitmap_from_pokemon(p,back)
        raise 'sprite size' unless b.bitmap.width == 160 && b.bitmap.height == 160
        b.dispose
      end
      raise 'icon path' unless GameData::Species.icon_filename_from_pokemon(p).include?('LAPRAS_1')
    end
    p.shiny = false
    before = Marshal.dump($player.pokedex)
    Tidebound::Opening.travel_coast(53,20)
    Tidebound::Opening.coast_camera_to(*Tidebound::Opening.coast_xy(55,22))
    Tidebound::Opening.lapras_visible = true
    Tidebound::Opening.lapras_alpha = 145
    pbWait(0.5)
    raise 'apparition registered in dex' unless before == Marshal.dump($player.pokedex)
    b = Graphics.snap_to_bitmap; b.to_file('lapras-pier.png'); b.dispose
    Tidebound::Opening.lapras_visible = false
    Tidebound::Opening.lapras_alpha = 0
    $player.party = [p]
    $lapras_battle_test = true
    WildBattle.start_core(Pokemon.new(:LAPRAS_1,10))
  rescue Exception => e
    raise if e.is_a?(SystemExit) && e.status == 0
    File.write('LAPRAS_FAIL.txt',e.full_message)
    exit(1)
  end
end
Scene_Map.prepend(LaprasTest)
module LaprasBattleView
  def pbCommandPhase(*args)
    return super unless $lapras_battle_test
    [0,1].each do |i|
      raise 'battle types' unless @battlers[i].pbHasType?(:WATER) && @battlers[i].pbHasType?(:GHOST)
    end
    12.times { Graphics.update; @scene.pbUpdate }
    b = Graphics.snap_to_bitmap; b.to_file('lapras-battle.png'); b.dispose
    File.write('LAPRAS_PASS.txt','PASS: native PBS compilation; form constructor and stock Lapras; inherited stats/moves/abilities; save and astral form/identity; normal/shiny front/back/icons; pier rendering without dex registration; Water/Ghost battle rendering.')
    exit
  rescue Exception => e
    raise if e.is_a?(SystemExit) && e.status == 0
    File.write('LAPRAS_FAIL.txt',e.full_message)
    exit(1)
  end
end
Battle.prepend(LaprasBattleView)
