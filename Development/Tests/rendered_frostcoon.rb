# TEST ONLY: inject before Main in a disposable native engine copy.
# Requires baseline 0.7.9 Data/species.dat copied as previous-species.dat.
module FrostInput
  def trigger?(key)
    return Graphics.frame_count % 6 == 0 if key == Input::USE
    super
  end
end
Input.singleton_class.prepend(FrostInput)
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('chosen-party.rxdata'))
  end
end
module FrostTest
  def update
    super
    return if @frost_checked || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @frost_checked = true
    paths = Dir.glob('PBS/pokemon*.txt').reject { |s| s =~ /pokemon_(forms|metrics)/ }
    Compiler.compile_pokemon(*paths)
    Compiler.compile_pokemon_forms(*Dir.glob('PBS/pokemon_forms*.txt'))
    expected = {HP:65,ATTACK:35,DEFENSE:95,SPECIAL_ATTACK:55,SPECIAL_DEFENSE:85,SPEED:15}
    data = GameData::Species.get(:FROSTCOON)
    raise 'stats' unless data.base_stats == expected
    raise 'ability' unless data.abilities == [:SHELLARMOR]
    # Construct an actual old-data individual, including cached old ability/stats.
    current = GameData::Species::DATA[:FROSTCOON]
    GameData::Species::DATA[:FROSTCOON] = Marshal.load(File.binread('previous-species.dat'))[:FROSTCOON]
    old = Pokemon.new(:FROSTCOON, 18)
    raise 'old fixture' unless old.ability_id == :SHEDSKIN
    GameData::Species::DATA[:FROSTCOON] = current
    old.name = 'Winter'; old.item = :ORANBERRY; old.hp = 3; old.status = :POISON
    old.moves.first.pp = 1
    identity = Tidebound.state.assign_identity(old)
    moves = old.moves.map { |m| [m.id,m.pp] }
    pid = old.personalID; iv = old.iv.dup; ev = old.ev.dup
    $player.party = [old]
    boxed = Marshal.load(Marshal.dump(old)); boxed.hp = 0
    $PokemonStorage[0,0] = boxed
    state = Tidebound.state
    state.souls << Tidebound::Soul.new('test-soul',boxed,{map_id:103,x:17,y:25},1)
    state.memorials << Tidebound::Soul.new('test-memorial',boxed,{map_id:103,x:17,y:25},1)
    save = Marshal.load(Marshal.dump(SaveData.compile_save_hash))
    SaveData.mark_values_as_unloaded
    SaveData.load_all_values(save)
    restored = $player.party.first
    raise 'saved refresh' unless restored.ability_id == :SHELLARMOR && restored.hp == 3 && restored.status == :POISON
    raise 'saved identity/moves' unless Tidebound.identity(restored)==identity && restored.personalID==pid && restored.iv==iv && restored.ev==ev && restored.item_id==:ORANBERRY && restored.name=='Winter' && restored.moves.map { |m| [m.id,m.pp] }==moves
    [$PokemonStorage[0,0],Tidebound.state.souls.last.pokemon,Tidebound.state.memorials.last.pokemon].each do |p|
      raise 'fainted holder revived or stale ability' unless p.hp==0 && p.ability_id==:SHELLARMOR
    end
    before = Marshal.dump(restored); Tidebound::Frostcoon.refresh_loaded
    raise 'repeat migration changed individual' unless before==Marshal.dump(restored)
    Tidebound::Opening.travel(103,17,25)
    p = pbGenerateWildPokemon(:WURMPLE,9); p.personalID = 5 << 16
    p.moves.clear; p.learn_move(:TACKLE); p.learn_move(:STRINGSHOT)
    id = Tidebound.state.assign_identity(p)
    p.level = 10
    raise 'split' unless p.check_evolution_on_level_up == :FROSTCOON
    p.item = :EVERSTONE
    raise 'Everstone' if p.check_evolution_on_level_up
    p.item = nil; p.level = 9
    $player.party = [p]
    ui = Object.new; def ui.pbRefresh; end; def ui.pbUpdate; end
    pbChangeLevel(p,10,ui)
    raise 'evolution' unless p.species==:FROSTCOON && p.form==0 && p.ability_id==:SHELLARMOR && Tidebound.identity(p)==id
    raise 'evolution moves' unless p.hasMove?(:HARDEN) && p.hasMove?(:POWDERSNOW)
    [55,100].each do |lv|
      check=Marshal.load(Marshal.dump(p));check.level=lv
      raise 'premature dragon' if check.check_evolution_on_level_up
    end
    [false,true].each do |shiny|
      p.shiny=shiny
      [false,true].each do |back|
        b=GameData::Species.sprite_bitmap_from_pokemon(p,back)
        raise 'asset dimensions' unless b.bitmap.width==160 && b.bitmap.height==160
        b.dispose
      end
      raise 'icon' unless GameData::Species.icon_filename_from_pokemon(p).include?('FROSTCOON')
    end
    stock=Pokemon.new(:WURMPLE,7);stock.personalID=5<<16
    raise 'stock changed' unless stock.check_evolution_on_level_up==:CASCOON
    sibling=Pokemon.new(:WURMPLE_1,10);sibling.personalID=0
    raise 'Glaciverm split' unless sibling.check_evolution_on_level_up==:GLACIVERM
    p.shiny=false;p.level=18;p.calc_stats;p.heal
    p.moves.clear;[:STRUGGLEBUG,:ICYWIND,:BUGBITE,:PROTECT].each { |m| p.learn_move(m) }
    $player.party=[p]
    $frost_battle=true
    WildBattle.start_core(:FROSTCOON,18)
  rescue Exception => e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('FROSTCOON_FAIL.txt',e.full_message);exit(1)
  end
end
Scene_Map.prepend(FrostTest)
module FrostBattle
  def pbCommandPhase(*args)
    return super unless $frost_battle
    user=@battlers[0];target=@battlers[1]
    raise 'typing' unless user.pbHasType?(:BUG) && user.pbHasType?(:ICE)
    raise '4x weaknesses' unless [:FIRE,:ROCK].all? { |t| Effectiveness.calculate(t,*user.pbTypes)==4.0 }
    raise 'Shell Armor crit protection' unless Battle::AbilityEffects.triggerCriticalCalcFromTarget(:SHELLARMOR,target,user,3)==-1
    12.times { Graphics.update; @scene.pbUpdate }
    b=Graphics.snap_to_bitmap;b.to_file('frostcoon-battle.png');b.dispose
    File.write('FROSTCOON_PASS.txt','PASS: PBS compilation; authored stats/ability; real old-data party/storage/soul/memorial save refresh; identity/HP/fainted/status/PP/moves/item preserved; migration idempotence; level-10 evolution animation and moves; fixed branch/Everstone; no premature dragon; normal/shiny front/back/icon assets; original and Glaciverm branches; battle rendering; native Shell Armor critical protection; Fire/Rock weaknesses.')
    exit
  rescue Exception => e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('FROSTCOON_FAIL.txt',e.full_message);exit(1)
  end
end
Battle.prepend(FrostBattle)
