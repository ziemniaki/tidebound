# Test only: inject before Main in a disposable native runtime.
module NivaInput
  def trigger?(key)
    return Graphics.frame_count%6==0 if key==Input::USE
    super
  end
end
Input.singleton_class.prepend(NivaInput)
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('chosen-party.rxdata'))
  end
end
module NivaTest
  def update
    super
    return if @niva_checked || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @niva_checked=true
    paths=Dir.glob('PBS/pokemon*.txt').reject { |s| s =~ /pokemon_(forms|metrics)/ }
    Compiler.compile_pokemon(*paths)
    Compiler.compile_pokemon_forms(*Dir.glob('PBS/pokemon_forms*.txt'))
    data=GameData::Species.get(:NIVALORA)
    raise 'stats' unless data.base_stats=={HP:100,ATTACK:45,DEFENSE:65,SPEED:145,SPECIAL_ATTACK:130,SPECIAL_DEFENSE:115}
    raise 'poison move' if (data.moves.map(&:last)+data.tutor_moves+data.egg_moves).any? { |m| GameData::Move.get(m).function_code.include?('Poison') }
    raise 'family' unless data.get_previous_species==:FROSTCOON && data.get_baby_species==:WURMPLE
    p=Pokemon.new(:FROSTCOON,54);p.name='Gentle';p.item=:ORANBERRY
    id=Tidebound.state.assign_identity(p);pid=p.personalID;iv=p.iv.dup;ev=p.ev.dup
    raise 'early' if p.check_evolution_on_level_up
    p.level=55;p.item=:EVERSTONE
    raise 'Everstone' if p.check_evolution_on_level_up
    p.item=:ORANBERRY
    raise 'threshold' unless p.check_evolution_on_level_up==:NIVALORA
    raise 'old over-level' unless Pokemon.new(:FROSTCOON,70).check_evolution_on_level_up==:NIVALORA
    p.level=54;p.calc_stats;p.moves.clear;p.learn_move(:WISH);p.learn_move(:SLEEPPOWDER)
    $player.party=[p]
    ui=Object.new;def ui.pbRefresh;end;def ui.pbUpdate;end
    pbChangeLevel(p,55,ui)
    raise 'evolution/type/ability' unless p.species==:NIVALORA && p.types==[:ICE,:DRAGON] && p.ability_id==:SHIELDDUST
    raise 'moves' unless [:WISH,:SLEEPPOWDER,:DRAGONBREATH,:ICEBEAM].all? { |m| p.hasMove?(m) }
    raise 'identity' unless Tidebound.identity(p)==id && p.personalID==pid && p.iv==iv && p.ev==ev && p.item_id==:ORANBERRY && p.name=='Gentle'
    raise 'unwanted evolution' if p.check_evolution_on_level_up
    p.hp=9;p.status=:POISON;p.moves.first.pp=2
    before=p.moves.map { |m| [m.id,m.pp] }
    $PokemonStorage[0,0]=Marshal.load(Marshal.dump(p));$PokemonStorage[0,0].hp=0
    save=Marshal.load(Marshal.dump(SaveData.compile_save_hash))
    SaveData.mark_values_as_unloaded;SaveData.load_all_values(save);p=$player.party.first
    raise 'save health/moves' unless p.species==:NIVALORA && p.hp==9 && p.status==:POISON && p.moves.map { |m| [m.id,m.pp] }==before
    raise 'box save' unless $PokemonStorage[0,0].species==:NIVALORA && $PokemonStorage[0,0].hp==0
    state=Tidebound::State.new;copy=Marshal.load(Marshal.dump(p));copy.hp=0
    state.enter_astral!([copy],{map_id:103,x:17,y:25})
    raise 'soul' unless state.begin_encounter!(id).species==:NIVALORA
    raise 'recovery' unless state.recover!(id).species==:NIVALORA
    [false,true].each do |shiny|
      p.shiny=shiny
      [false,true].each do |back|
        b=GameData::Species.sprite_bitmap_from_pokemon(p,back)
        raise 'art' unless b.bitmap.width==160 && b.bitmap.height==160;b.dispose
      end
      raise 'icon' unless GameData::Species.icon_filename_from_pokemon(p).include?('NIVALORA')
    end
    a=Pokemon.new(:WURMPLE_1,10);a.personalID=0
    b=Pokemon.new(:WURMPLE_1,10);b.personalID=5<<16
    raise 'branches' unless a.check_evolution_on_level_up==:GLACIVERM && b.check_evolution_on_level_up==:FROSTCOON
    stock=Pokemon.new(:WURMPLE,7);stock.personalID=5<<16
    raise 'stock' unless stock.check_evolution_on_level_up==:CASCOON
    Tidebound::Opening.travel(103,17,25);p.shiny=false;p.heal;$niva_battle=true
    WildBattle.start_core(:NIVALORA,55)
  rescue Exception=>e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('NIVALORA_FAIL.txt',e.full_message);exit(1)
  end
end
Scene_Map.prepend(NivaTest)
module NivaBattle
  def pbCommandPhase(*args)
    return super unless $niva_battle
    u=@battlers[0];t=@battlers[1]
    move=proc { |m| Battle::Move.from_pokemon_move(self,Pokemon::Move.new(m)) }
    raise 'typing' unless u.pbTypes==[:ICE,:DRAGON]
    raise 'Shield Dust' unless move.call(:ICEBEAM).pbAdditionalEffectChance(t,u)==0
    dance=move.call(:DRAGONDANCE);dance.pbEffectGeneral(u)
    raise 'Dragon Dance' unless u.stages[:ATTACK]==1 && u.stages[:SPEED]==1
    move.call(:QUIVERDANCE).pbEffectGeneral(u)
    raise 'Quiver Dance' unless u.stages[:SPECIAL_ATTACK]==1 && u.stages[:SPECIAL_DEFENSE]==1 && u.stages[:SPEED]==2
    u.hp=10;u.status=:POISON
    move.call(:ROOST).pbEffectGeneral(u)
    raise 'Roost HP/status' unless u.hp>10 && u.status==:POISON && u.pbHasType?(:ICE) && u.pbHasType?(:DRAGON)
    move.call(:SLEEPPOWDER).pbEffectAgainstTarget(u,t)
    raise 'sleep' unless t.status==:SLEEP
    12.times { Graphics.update;@scene.pbUpdate }
    bitmap=Graphics.snap_to_bitmap;bitmap.to_file('nivalora-battle.png');bitmap.dispose
    File.write('NIVALORA_PASS.txt','PASS: PBS compilation, 600 stats, no poisoning moves, ancestry; 54/55 threshold, Everstone, overlevel saves; actual evolution with both moves/identity; save/box/astral; normal/shiny front/back/icons; Wurmple splits; battle rendering; Shield Dust, Dragon Dance, Quiver Dance, Roost without poison cure, Sleep Powder.')
    exit
  rescue Exception=>e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('NIVALORA_FAIL.txt',e.full_message);exit(1)
  end
end
Battle.prepend(NivaBattle)
