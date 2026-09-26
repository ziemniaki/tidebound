# Historical 0.7.5 fixture. Evolution assertions superseded by rendered_glaciverm.rb.
# TEST ONLY: inject before Main in a disposable native engine directory.
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('chosen-party.rxdata'))
  end
end
module WurmpleTest
  def update
    super
    return if @wurmple_checked || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @wurmple_checked = true
    old = Pokemon.new(:WURMPLE, 5)
    Tidebound::Opening.travel(103, 17, 25)
    p = pbGenerateWildPokemon(:WURMPLE, 5)
    raise 'forest form/type' unless p.form == 1 && p.types == [:BUG, :ICE]
    raise 'old companion changed' unless old.form == 0 && old.types == [:BUG]
    base = GameData::Species.get(:WURMPLE)
    [:base_stats, :moves, :abilities, :hidden_abilities, :evolutions].each do |field|
      raise "inherited #{field}" unless p.species_data.send(field) == base.send(field)
    end
    id = Tidebound.state.assign_identity(p)
    copy = Marshal.load(Marshal.dump(p))
    raise 'save form' unless copy.form == 1 && copy.types == [:BUG, :ICE]
    souls = Tidebound::State.new
    copy.hp = 0
    souls.enter_astral!([copy], {map_id: 103, x: 17, y: 25})
    raise 'spirit form' unless souls.begin_encounter!(id).form == 1
    raise 'recovery form' unless souls.recover!(id).form == 1
    {0 => :SILCOON, (5 << 16) => :CASCOON}.each do |pid, target|
      evo = Marshal.load(Marshal.dump(p))
      evo.personalID = pid
      evo.level = 6
      raise 'early evolution' if evo.check_evolution_on_level_up
      evo.level = 7
      raise 'branch' unless evo.check_evolution_on_level_up == target
      evo.item = :EVERSTONE
      raise 'Everstone' if evo.check_evolution_on_level_up
      evo.item = nil
      evo.species = target
      raise 'undefined evolved form' unless evo.form == 0 && evo.types == [:BUG]
      raise 'evolution identity' unless Tidebound.identity(evo) == id
    end
    Tidebound::Opening.travel(108, 30, 18)
    other = pbGenerateWildPokemon(:WURMPLE, 5)
    raise 'other map' unless other.form == 0 && other.types == [:BUG]
    [false, true].each do |shiny|
      p.shiny = shiny
      [false, true].each do |back|
        b = GameData::Species.sprite_bitmap_from_pokemon(p, back)
        raise 'sprite size' unless b.bitmap.width == 160 && b.bitmap.height == 160
        b.dispose
      end
      raise 'regional icon' unless GameData::Species.icon_filename_from_pokemon(p).include?('WURMPLE_1')
    end
    p.shiny = false
    p.heal
    $player.party = [p]
    Tidebound::Opening.travel(103, 17, 25)
    $wurmple_battle_test = true
    WildBattle.start_core(:WURMPLE, 5)
  rescue Exception => e
    raise if e.is_a?(SystemExit) && e.status == 0
    File.write('WURMPLE_FAIL.txt', e.full_message)
    exit(1)
  end
end
Scene_Map.prepend(WurmpleTest)

module WurmpleBattleView
  def pbCommandPhase(*args)
    return super unless $wurmple_battle_test
    [0, 1].each do |i|
      raise 'battle typing' unless @battlers[i].pbHasType?(:BUG) && @battlers[i].pbHasType?(:ICE)
    end
    12.times { Graphics.update; @scene.pbUpdate }
    b = Graphics.snap_to_bitmap
    b.to_file('wurmple-battle.png')
    b.dispose
    File.write('WURMPLE_PASS.txt', 'PASS: forest selection, Bug/Ice, inherited data, stock companions/other maps, save/astral recovery, both level-7 branches, Everstone, evolution identity/form normalization, normal/shiny battle and icon asset loading; actual Bug/Ice battle rendered.')
    exit
  end
end
Battle.prepend(WurmpleBattleView)
