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
    f=Tidebound::FieldDetails;o=Tidebound::Opening
    p=$player.party.first
    raise 'old companion missing' unless p.species==:MAKUHITA
    id=Tidebound.identity(p);p.hp=1;p.status=:POISON;p.moves.each { |m| m.pp=0 }
    raise 'first fire' unless f.heal_fire(:wood_fire,1000) && p.hp==p.totalhp && p.moves.all? { |m| m.pp==m.total_pp }
    raise 'poison cured' unless p.status==:POISON
    p.hp=1
    raise 'early repeat' if f.heal_fire(:wood_fire,1899)
    raise 'cooldown healed' unless p.hp==1
    raise 'independent fire' unless f.heal_fire(:road_fire,1100)
    $tidebound=Marshal.load(Marshal.dump(Tidebound.state))
    raise 'save timer' unless f.remaining(:wood_fire,1899)==1
    raise '900s boundary' unless f.heal_fire(:wood_fire,1900)
    raise 'other timer changed' unless f.remaining(:road_fire,1900)==100
    raise 'identity' unless Tidebound.identity(p)==id
    o.travel_coast(8,16);shot('lighthouse')
    o.travel_coast(22,12);shot('shop')
    o.travel(103,17,25);shot('wood-exit')
    o.travel(103,9,18);shot('wood-grass')
    raise 'grass tag' unless $game_map.terrain_tag(6,16).land_wild_encounters
    raise 'safe path' if $game_map.terrain_tag(17,20).land_wild_encounters
    e=GameData::Encounter.get(103);raise 'forest species' unless e.types[:Land].all? { |r| GameData::Species.get(r[1]).types.include?(:BUG) }
    before=$bag.quantity(:ORANBERRY);f.berry(103,12,19,:ORANBERRY)
    raise 'berry pickup' unless $bag.quantity(:ORANBERRY)==before+2
    f.berry(103,12,19,:ORANBERRY)
    raise 'duplicate berry' unless $bag.quantity(:ORANBERRY)==before+2
    o.travel(108,30,18);shot('road-grass')
    raise 'road roster' unless GameData::Encounter.get(108).types[:Land].map { |r| r[1] }.sort==[:ZIGZAGOON,:SUNKERN,:EKANS].sort
    raise 'grass disabled' unless $PokemonEncounters.encounter_possible_here?
    o.travel(108,26,40);shot('road-fire');o.travel(108,35,42);shot('storehouse')
    p.heal;o.travel(103,7,17)
    raise 'forest grass disabled' unless $PokemonEncounters.encounter_possible_here?
    # Test the actual step encounter path; make only the trigger deterministic.
    def $PokemonEncounters.encounter_triggered?(*args);true;end
    $field_battle=true
    pbBattleOnStepTaken(false)
    raise 'native grass battle did not start'
  rescue Exception=>e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('FIELD_FAIL.txt',e.full_message);exit(1)
  end
end
Scene_Map.prepend(FieldView)
module FieldBattleView
  def pbStartBattle(*args)
    super
    return unless $field_battle
    raise 'wrong loss wrapper' unless Tidebound.battle_context==:living
    raise 'daytime battle' unless @battle.time==2
    6.times { Graphics.update;pbUpdate }
    b=Graphics.snap_to_bitmap;b.to_file('field-battle.png');b.dispose
    File.write('FIELD_PASS.txt','PASS: retained save; independent timed HP/PP recovery/status/identity/persistence; berry collection; grass tables/terrain/safe path; native step battle through living wrapper; night rendering.')
    exit
  end
end
Battle::Scene.prepend(FieldBattleView)
