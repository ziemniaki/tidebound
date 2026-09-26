# TEST ONLY: disposable engine and retained save; never embed in a release.
module SunkernInput
  def trigger?(key)
    return Graphics.frame_count%6==0 if key==Input::USE
    super
  end
end
Input.singleton_class.prepend(SunkernInput)
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('chosen-party.rxdata'))
  end
end
module SunkernTest
  def update
    super
    return if @sunkern_checked || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @sunkern_checked=true;o=Tidebound::Opening
    o.travel(108,30,18);p=pbGenerateWildPokemon(:SUNKERN,5)
    raise 'regional type' unless p.form==1 && p.types==[:GRASS,:DARK]
    raise 'early moves' unless p.moves.map(&:id)==[:ABSORB,:GROWTH,:PAYBACK]
    raise 'base stats changed' unless p.baseStats.values.all? { |x| x==30 }
    raise 'icon fallback' unless GameData::Species.icon_filename_from_pokemon(p).include?('SUNKERN_1')
    [false,true].each do |shiny|
      p.shiny=shiny
      [false,true].each do |back|
        b=GameData::Species.sprite_bitmap_from_pokemon(p,back)
        raise 'sprite dimensions' unless b.bitmap.width==160 && b.bitmap.height==160
        b.dispose
      end
    end
    p.shiny=false;p.name='Little Reed';p.item=:ORANBERRY
    restored=Marshal.load(Marshal.dump(p))
    raise 'save roundtrip' unless restored.form==1 && restored.name==p.name && restored.personalID==p.personalID && restored.item_id==:ORANBERRY
    o.travel(103,17,25)
    raise 'form changed outside road' unless restored.form==1
    raise 'ordinary form overwritten' unless pbGenerateWildPokemon(:SUNKERN,5).form==0
    restored.level=24
    raise 'evolution blocked' unless restored.check_evolution_on_level_up==:MOONKERN
    restored.species=:MOONKERN
    raise 'invalid evolved form' unless restored.form==0 && restored.types==[:GRASS,:GHOST]
    s=Tidebound::State.new;s.assign_identity(p);p.hp=0
    s.enter_astral!([p],{map_id:108,x:30,y:18})
    soul=s.souls.first;foe=s.begin_encounter!(soul.id)
    raise 'spirit form lost' unless foe.form==1
    recovered=s.recover!(soul.id)
    raise 'recovery lost form or moves' unless recovered.form==1 && recovered.moves.map(&:id)==[:ABSORB,:GROWTH,:PAYBACK]
    o.travel(108,30,18);recovered.heal;$player.party=[recovered]
    $sunkern_battle=true;WildBattle.start_core(:SUNKERN,5)
  rescue Exception=>e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('SUNKERN_FAIL.txt',e.full_message);exit(1)
  end
end
Scene_Map.prepend(SunkernTest)
module SunkernBattleTest
  def pbStartBattle(*args)
    super
    return unless $sunkern_battle
    raise 'wrong battle form' unless @battle.battlers[1].pokemon.form==1
    raise 'wrong battle type' unless @battle.battlers[1].pbHasType?(:DARK)
    raise 'day battle' unless @battle.time==2
  end
end
Battle::Scene.prepend(SunkernBattleTest)
module SunkernCommandView
  def pbCommandPhase(*args)
    return super unless $sunkern_battle
    12.times { Graphics.update;@scene.pbUpdate }
    b=Graphics.snap_to_bitmap;b.to_file('sunkern-battle.png');b.dispose
    File.write('SUNKERN_PASS.txt','PASS: native regional encounter/type/moves; original stats/form; assets/shiny paths; save identity; astral recovery; Moonkern evolution; actual night battle front/back rendering.')
    exit
  end
end
Battle.prepend(SunkernCommandView)
