# TEST ONLY in a disposable engine copy.
module FloraInput
  def trigger?(key)
    return Graphics.frame_count%6==0 if key==Input::USE
    super
  end
end
Input.singleton_class.prepend(FloraInput)
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('chosen-party.rxdata'))
  end
end
module FloraTest
  def update
    super
    return if @flora_checked || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @flora_checked=true;o=Tidebound::Opening;o.travel(108,30,18)
    p=pbGenerateWildPokemon(:SUNKERN,13);p.name='Little Reed';p.item=:ORANBERRY
    id=Tidebound.state.assign_identity(p);pid=p.personalID
    ui=Object.new
    def ui.pbRefresh;end
    def ui.pbUpdate;end
    raise 'early Sunkern' if p.check_evolution_on_level_up
    $player.party=[p];pbChangeLevel(p,14,ui)
    raise 'first evolution' unless p.species==:MOONKERN && p.form==0 && p.hasMove?(:HEX)
    p.level=19;p.calc_stats;p.reset_moves
    raise 'early Moonkern' if p.check_evolution_on_level_up
    p.level=20;p.calc_stats;p.item=:EVERSTONE
    raise 'Everstone' if p.check_evolution_on_level_up
    p.item=:ORANBERRY
    raise '20 rule' unless p.check_evolution_on_level_up==:MOONFLORA
    p.level=19;p.calc_stats;pbChangeLevel(p,20,ui)
    raise 'second evolution' unless p.species==:MOONFLORA && p.form==0 && p.hasMove?(:SHADOWBALL)
    raise 'identity' unless Tidebound.identity(p)==id && p.personalID==pid && p.name=='Little Reed' && p.item_id==:ORANBERRY
    raise 'type/stats' unless p.types==[:GRASS,:GHOST] && p.baseStats.values.sum==490
    raise 'final species' if p.check_evolution_on_level_up
    raise 'old Moonkern' unless Pokemon.new(:MOONKERN,25).check_evolution_on_level_up==:MOONFLORA
    copy=Marshal.load(Marshal.dump(p));raise 'save' unless copy.species==:MOONFLORA && copy.personalID==pid
    s=Tidebound::State.new;copy.hp=0;s.enter_astral!([copy],{map_id:108,x:30,y:18})
    raise 'spirit' unless s.begin_encounter!(id).species==:MOONFLORA
    raise 'recovery' unless s.recover!(id).species==:MOONFLORA
    o.travel(103,17,25);normal=pbGenerateWildPokemon(:SUNKERN,20)
    raise 'stock changed' unless normal.form==0 && normal.check_evolution_on_use_item(:SUNSTONE)==:SUNFLORA
    raise 'family' unless GameData::Species.get(:MOONFLORA).get_previous_species==:MOONKERN && GameData::Species.get(:MOONFLORA).get_baby_species==:SUNKERN
    [false,true].each do |shiny|
      p.shiny=shiny
      [false,true].each do |back|
        b=GameData::Species.sprite_bitmap_from_pokemon(p,back);raise 'sprite' unless b.bitmap.width==160;b.dispose
      end
    end
    p.shiny=false
    raise 'icon' unless GameData::Species.icon_filename_from_pokemon(p).include?('MOONFLORA')
    o.travel(108,30,18);p.heal;$flora_battle=true;WildBattle.start_core(:MOONFLORA,20)
  rescue Exception=>e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('MOONFLORA_FAIL.txt',e.full_message);exit(1)
  end
end
Scene_Map.prepend(FloraTest)
module FloraBattleView
  def pbCommandPhase(*args)
    return super unless $flora_battle
    raise 'battle type' unless @battlers[1].pbHasType?(:GHOST)
    12.times { Graphics.update;@scene.pbUpdate }
    b=Graphics.snap_to_bitmap;b.to_file('moonflora-battle.png');b.dispose
    File.write('MOONFLORA_PASS.txt','PASS: native 13/14 and 19/20 boundaries; both real evolutions and moves; Everstone; old higher-level Moonkern; identity/item; stock Sun Stone; save/astral; family; normal/shiny art; native battle.')
    exit
  end
end
Battle.prepend(FloraBattleView)
