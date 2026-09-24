# TEST ONLY: disposable native engine; no user saves modified.
module MoonInput
  def trigger?(key)
    return Graphics.frame_count%6==0 if key==Input::USE
    return true if key==Input::BACK && $moon_cancel
    super
  end
end
Input.singleton_class.prepend(MoonInput)
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('chosen-party.rxdata'))
  end
end
module MoonTest
  def update
    super
    return if @moon_checked || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @moon_checked=true;o=Tidebound::Opening;o.travel(108,30,18)
    p=pbGenerateWildPokemon(:SUNKERN,13);p.name='Little Reed';p.item=:ORANBERRY
    id=Tidebound.state.assign_identity(p);pid=p.personalID
    raise 'early evolution' if p.check_evolution_on_level_up
    p.level=14;p.calc_stats
    raise 'wrong evolution' unless p.check_evolution_on_level_up==:MOONKERN
    p.item=:EVERSTONE
    raise 'Everstone ignored' if p.check_evolution_on_level_up
    p.item=:ORANBERRY
    # Cancel the real native evolution screen, then retry through real level gain.
    e=PokemonEvolutionScene.new;e.pbStartScreen(p,:MOONKERN)
    $moon_cancel=true;e.pbEvolution;$moon_cancel=false;e.pbEndScreen
    raise 'cancel destroyed Pokemon' unless p.species==:SUNKERN && p.form==1
    File.write('MOON_STAGE.txt','cancel passed; level up next')
    p.level=13;p.calc_stats;$player.party=[p]
    ui=Object.new
    def ui.pbRefresh;end
    def ui.pbUpdate;end
    File.write('MOON_STAGE.txt','calling pbChangeLevel')
    pbChangeLevel(p,14,ui)
    File.write('MOON_STAGE.txt','level up and evolution returned')
    raise 'evolution identity' unless p.species==:MOONKERN && p.form==0 && p.personalID==pid && Tidebound.identity(p)==id && p.name=='Little Reed' && p.item_id==:ORANBERRY
    raise 'types' unless p.types==[:GRASS,:GHOST]
    raise 'stats' unless p.baseStats.values.sum==440 && p.baseStats[:SPECIAL_ATTACK]==105
    raise 'evolution move' unless p.hasMove?(:HEX)
    raise 'abilities' unless [:INSOMNIA,:INFILTRATOR,:CURSEDBODY].include?(p.ability_id)
    raise 'regional Sun Stone path retained' if pbGenerateWildPokemon(:SUNKERN,24).check_evolution_on_use_item(:SUNSTONE)
    o.travel(103,17,25);normal=pbGenerateWildPokemon(:SUNKERN,24)
    raise 'ordinary Sunkern changed' unless normal.form==0 && normal.check_evolution_on_use_item(:SUNSTONE)==:SUNFLORA && !normal.check_evolution_on_level_up
    copy=Marshal.load(Marshal.dump(p))
    raise 'save species/identity' unless copy.species==:MOONKERN && copy.form==0 && copy.personalID==pid && copy.hasMove?(:HEX)
    s=Tidebound::State.new;copy.hp=0;s.enter_astral!([copy],{map_id:108,x:30,y:18})
    foe=s.begin_encounter!(id);raise 'spirit species' unless foe.species==:MOONKERN
    recovered=s.recover!(id);raise 'recovery species' unless recovered.species==:MOONKERN && recovered.hasMove?(:HEX)
    [false,true].each do |shiny|
      p.shiny=shiny
      [false,true].each do |back|
        b=GameData::Species.sprite_bitmap_from_pokemon(p,back);raise 'sprite' unless b.bitmap.width==160;b.dispose
      end
    end
    p.shiny=false
    raise 'icon' unless GameData::Species.icon_filename_from_pokemon(p).include?('MOONKERN')
    raise 'family' unless GameData::Species.get(:MOONKERN).get_previous_species==:SUNKERN
    o.travel(108,30,18);p.heal;$moon_battle=true
    WildBattle.start_core(:MOONKERN,24)
  rescue Exception=>e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('MOONKERN_FAIL.txt',e.full_message);exit(1)
  end
end
Scene_Map.prepend(MoonTest)
module MoonBattleView
  def pbCommandPhase(*args)
    return super unless $moon_battle
    raise 'battle types' unless @battlers[1].pbHasType?(:GHOST) && @battlers[1].pbHasType?(:GRASS)
    12.times { Graphics.update;@scene.pbUpdate }
    b=Graphics.snap_to_bitmap;b.to_file('moonkern-battle.png');b.dispose
    File.write('MOONKERN_PASS.txt','PASS: level 13/14 boundary; Everstone; actual evolution cancellation and level-up retry; Hex; form0/type/stats/ability; identity/item; stock Sun Stone; save roundtrip; astral recovery; sprite/icon/shiny loaders; native night battle front/back.')
    exit
  end
end
Battle.prepend(MoonBattleView)

module MoonWatchdog
  def update(*args)
    super
    @moon_watch_start ||= System.uptime
    if System.uptime-@moon_watch_start > 55 && !@moon_watch_done
      @moon_watch_done=true
      b=Graphics.snap_to_bitmap;b.to_file('moon-progress.png');b.dispose
      File.write('MOON_STACK.txt',caller.join("\n"))
    end
  end
end
Graphics.singleton_class.prepend(MoonWatchdog)
