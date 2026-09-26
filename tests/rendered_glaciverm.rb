# TEST ONLY. Inject before Main in a disposable native engine copy.
module GlaciInput
  def trigger?(key)
    return Graphics.frame_count % 6 == 0 if key == Input::USE
    super
  end
end
Input.singleton_class.prepend(GlaciInput)
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('chosen-party.rxdata'))
  end
end
module GlaciTest
  def update
    super
    return if @glaci_checked || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @glaci_checked = true
    # Exercise the real PBS compiler in this disposable copy, so rebuilding in
    # Essentials cannot silently restore the old evolutionary branches.
    paths = Dir.glob('PBS/pokemon*.txt').reject { |s| s =~ /pokemon_(forms|metrics)/ }
    Compiler.compile_pokemon(*paths)
    Compiler.compile_pokemon_forms(*Dir.glob('PBS/pokemon_forms*.txt'))
    Tidebound::Opening.travel(103, 17, 25)
    ui = Object.new
    def ui.pbRefresh; end
    def ui.pbUpdate; end
    results = []
    {0 => :GLACIVERM, (5 << 16) => :FROSTCOON}.each do |pid, target|
      p = pbGenerateWildPokemon(:WURMPLE, 9)
      p.personalID = pid
      p.name = 'Little Frost'
      p.item = :ORANBERRY
      p.ability_index = 2
      p.moves.clear
      p.learn_move(:TACKLE)
      p.learn_move(:STRINGSHOT)
      id = Tidebound.state.assign_identity(p)
      raise 'premature evolution' if p.check_evolution_on_level_up
      p.level = 10
      3.times { raise 'unstable branch' unless p.check_evolution_on_level_up == target }
      saved = Marshal.load(Marshal.dump(p))
      raise 'save branch' unless saved.check_evolution_on_level_up == target
      p.item = :EVERSTONE
      raise 'Everstone' if p.check_evolution_on_level_up
      p.item = :ORANBERRY
      p.level = 9
      $player.party = [p]
      pbChangeLevel(p, 10, ui)
      raise 'evolution/form' unless p.species == target && p.form == 0
      raise 'identity/held item' unless Tidebound.identity(p) == id && p.personalID == pid && p.name == 'Little Frost' && p.item_id == :ORANBERRY
      if target == :GLACIVERM
        raise 'type/stats/ability' unless p.types == [:ICE, :BUG] && p.baseStats.values.sum == 435 && p.ability_id == :TECHNICIAN
        raise 'evolution moves' unless p.hasMove?(:BUGBITE) && p.hasMove?(:ICESHARD)
      else
        raise 'cocoon type' unless p.types == [:BUG, :ICE]
        raise 'cocoon moves' unless p.hasMove?(:HARDEN) && p.hasMove?(:POWDERSNOW)
      end
      [55, 100].each do |lv|
        check = Marshal.load(Marshal.dump(p)); check.level = lv
        raise 'unimplemented further evolution' if check.check_evolution_on_level_up
      end
      copy = Marshal.load(Marshal.dump(p))
      souls = Tidebound::State.new
      copy.hp = 0
      souls.enter_astral!([copy], {map_id:103,x:17,y:25})
      raise 'spirit species' unless souls.begin_encounter!(id).species == target
      raise 'recovery identity' unless Tidebound.identity(souls.recover!(id)) == id
      [false, true].each do |shiny|
        p.shiny = shiny
        [false, true].each do |back|
          b = GameData::Species.sprite_bitmap_from_pokemon(p, back)
          raise 'sprite canvas' unless b.bitmap.width == 160 && b.bitmap.height == 160
          b.dispose
        end
        raise 'icon asset' unless GameData::Species.icon_filename_from_pokemon(p).include?(target.to_s)
      end
      p.shiny = false
      results << p
    end
    # Previously owned regional Wurmple already above 10 qualify next level.
    old = Pokemon.new(:WURMPLE, 15); old.form = 1; old.personalID = 0
    raise 'old higher-level individual' unless old.check_evolution_on_level_up == :GLACIVERM
    {0 => :SILCOON, (5 << 16) => :CASCOON}.each do |pid, target|
      stock = Pokemon.new(:WURMPLE, 7); stock.personalID = pid
      raise 'stock branch changed' unless stock.form == 0 && stock.check_evolution_on_level_up == target
    end
    raise 'Moonflora changed' unless Pokemon.new(:MOONKERN, 20).check_evolution_on_level_up == :MOONFLORA
    p = results.first
    p.level = 24; p.calc_stats; p.heal
    p.moves.clear
    [:BUGBITE,:ICESHARD,:FIRSTIMPRESSION,:COIL].each { |m| p.learn_move(m) }
    $player.party = [p]
    $glaci_battle = true
    WildBattle.start_core(:GLACIVERM, 24)
  rescue Exception => e
    raise if e.is_a?(SystemExit) && e.status == 0
    File.write('GLACIVERM_FAIL.txt', e.full_message)
    exit(1)
  end
end
Scene_Map.prepend(GlaciTest)
module GlaciBattleView
  def pbCommandPhase(*args)
    return super unless $glaci_battle
    user = @battlers[0]; target = @battlers[1]
    raise 'Fire/Rock matchup' unless [:FIRE,:ROCK].all? { |t| Effectiveness.calculate(t,*user.pbTypes) == 4.0 }
    {BUGBITE:1.5, ICESHARD:1.5, ICEFANG:1.0, FIRSTIMPRESSION:1.0}.each do |id, expected|
      move = Battle::Move.from_pokemon_move(self, Pokemon::Move.new(id))
      mults = {power_multiplier:1.0}
      Battle::AbilityEffects.triggerDamageCalcFromUser(:TECHNICIAN,user,target,move,mults,move.power,move.type)
      raise "Technician #{id}" unless mults[:power_multiplier] == expected
    end
    raise 'Ice Shard priority' unless GameData::Move.get(:ICESHARD).priority == 1
    first = Battle::Move.from_pokemon_move(self, Pokemon::Move.new(:FIRSTIMPRESSION))
    raise 'First Impression priority' unless first.priority == 2
    user.turnCount = 1
    raise 'first turn failed' if first.pbMoveFailed?(user, [target])
    user.turnCount = 2
    raise 'later turn succeeded' unless first.pbMoveFailed?(user, [target])
    coil = Battle::Move.from_pokemon_move(self, Pokemon::Move.new(:COIL))
    coil.pbEffectGeneral(user)
    raise 'Coil effect' unless [:ATTACK,:DEFENSE,:ACCURACY].all? { |s| user.stages[s] == 1 }
    12.times { Graphics.update; @scene.pbUpdate }
    b=Graphics.snap_to_bitmap; b.to_file('glaciverm-battle.png'); b.dispose
    File.write('GLACIVERM_PASS.txt', 'PASS: real PBS recompile; native level-10 split and both evolution animations; learned moves; fixed branch/save/Everstone; hidden-ability fallback; identity/item/astral preservation; stock branches; old high-level regional; no fake dragon; normal/shiny front/back/icons; Technician thresholds; priorities and First Impression first-turn restriction; Coil stages; 4x Fire/Rock; actual battle rendering.')
    exit
  rescue Exception => e
    raise if e.is_a?(SystemExit) && e.status == 0
    File.write('GLACIVERM_FAIL.txt', e.full_message)
    exit(1)
  end
end
Battle.prepend(GlaciBattleView)
