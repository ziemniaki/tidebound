# TEST ONLY: inject before Main in a disposable native engine copy.
module FrostSupportInput
  def trigger?(key)
    return Graphics.frame_count % 6 == 0 if key == Input::USE
    super
  end
end
Input.singleton_class.prepend(FrostSupportInput)
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('chosen-party.rxdata'))
  end
end
module FrostSupportTest
  def update
    super
    return if @frost_checked || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @frost_checked = true
    paths = Dir.glob('PBS/pokemon*.txt').reject { |s| s =~ /pokemon_(forms|metrics)/ }
    Compiler.compile_pokemon(*paths)
    Compiler.compile_pokemon_forms(*Dir.glob('PBS/pokemon_forms*.txt'))
    data = GameData::Species.get(:FROSTCOON)
    raise 'damaging compatibility' unless (data.moves.map(&:last)+data.tutor_moves+data.egg_moves).all? { |m| GameData::Move.get(m).category==2 }
    old=Pokemon.new(:FROSTCOON,18)
    old.instance_variable_set(:@tidebound_frostcoon_revision,1)
    old.name='Winter';old.item=:ORANBERRY;old.hp=3;old.status=:POISON
    old.moves.clear
    [:TACKLE,:HARDEN,:POWDERSNOW,:BUGBITE].each { |m| old.learn_move(m) }
    [0,7,3,2].each_with_index { |pp,i| old.moves[i].pp=pp }
    identity=Tidebound.state.assign_identity(old)
    pid=old.personalID;iv=old.iv.dup;ev=old.ev.dup
    $player.party=[old]
    boxed=Marshal.load(Marshal.dump(old));boxed.hp=0
    $PokemonStorage[0,0]=boxed
    provisional=Marshal.load(Marshal.dump(boxed))
    provisional.instance_variable_set(:@tidebound_frostcoon_revision,0)
    provisional.ability=:SHEDSKIN
    $PokemonStorage[0,1]=provisional
    state=Tidebound.state
    state.souls << Tidebound::Soul.new('test-soul',boxed,{map_id:103,x:17,y:25},1)
    state.memorials << Tidebound::Soul.new('test-memorial',boxed,{map_id:103,x:17,y:25},1)
    save=Marshal.load(Marshal.dump(SaveData.compile_save_hash))
    SaveData.mark_values_as_unloaded;SaveData.load_all_values(save)
    restored=$player.party.first
    expected=[[:SPIKES,0],[:HARDEN,7],[:WISH,3],[:STUNSPORE,2]]
    raise 'move/PP migration' unless restored.moves.map { |m| [m.id,m.pp] }==expected
    raise 'saved health' unless restored.hp==3 && restored.status==:POISON
    raise 'saved identity' unless Tidebound.identity(restored)==identity && restored.personalID==pid && restored.iv==iv && restored.ev==ev && restored.item_id==:ORANBERRY && restored.name=='Winter'
    [$PokemonStorage[0,0],$PokemonStorage[0,1],Tidebound.state.souls.last.pokemon,Tidebound.state.memorials.last.pokemon].each do |p|
      raise 'fainted holder' unless p.hp==0 && p.ability_id==:SHELLARMOR && p.moves.map { |m| [m.id,m.pp] }==expected
    end
    supportive=Pokemon.new(:FROSTCOON,40);supportive.moves.clear
    [:WISH,:STICKYWEB,:RAINDANCE,:PROTECT].each { |m| supportive.learn_move(m) }
    supportive.moves.each { |m| m.pp=2 };selected=supportive.moves.map { |m| [m.id,m.pp] }
    Tidebound::Frostcoon.refresh(supportive)
    raise 'selected support lost' unless selected==supportive.moves.map { |m| [m.id,m.pp] }
    before=Marshal.dump(restored);Tidebound::Frostcoon.refresh_loaded
    raise 'not idempotent' unless before==Marshal.dump(restored)
    Tidebound::Opening.travel(103,17,25)
    p=pbGenerateWildPokemon(:WURMPLE,9);p.personalID=5<<16
    p.moves.clear;[:TACKLE,:STRINGSHOT,:POISONSTING].each { |m| p.learn_move(m) }
    $player.party=[p]
    ui=Object.new;def ui.pbRefresh;end;def ui.pbUpdate;end
    pbChangeLevel(p,10,ui)
    raise 'evolution' unless p.species==:FROSTCOON && p.hasMove?(:SPIKES) && p.hasMove?(:WISH) && p.hasMove?(:STRINGSHOT)
    raise 'inherited attack' unless p.moves.all? { |m| GameData::Move.get(m.id).category==2 }
    p.level=40;p.calc_stats;p.heal
    p.moves.clear;[:SPIKES,:WISH,:STUNSPORE,:RAINDANCE].each { |m| p.learn_move(m) }
    teammate=Pokemon.new(:NATU,40);teammate.hp=5;teammate.status=:POISON
    $player.party=[p,teammate];$frost_support_battle=true
    WildBattle.start_core(:ZIGZAGOON,40)
  rescue Exception => e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('FROSTCOON_SUPPORT_FAIL.txt',e.full_message);exit(1)
  end
end
Scene_Map.prepend(FrostSupportTest)
module FrostSupportBattle
  def pbCommandPhase(*args)
    return super unless $frost_support_battle
    user=@battlers[0];target=@battlers[1]
    move=proc { |id| Battle::Move.from_pokemon_move(self,Pokemon::Move.new(id)) }
    [:SPIKES,:STICKYWEB].each { |id| move.call(id).pbEffectGeneral(user) }
    raise 'hazards' unless target.pbOwnSide.effects[PBEffects::Spikes]==1 && target.pbOwnSide.effects[PBEffects::StickyWeb]
    move.call(:RAINDANCE).pbEffectGeneral(user)
    raise 'rain' unless user.effectiveWeather==:Rain
    veil=move.call(:AURORAVEIL)
    raise 'veil without hail' unless veil.pbMoveFailed?(user,[user])
    move.call(:HAIL).pbEffectGeneral(user)
    raise 'hail' unless user.effectiveWeather==:Hail
    raise 'veil in hail failed' if veil.pbMoveFailed?(user,[user])
    veil.pbEffectGeneral(user)
    raise 'veil missing' unless user.pbOwnSide.effects[PBEffects::AuroraVeil]>0
    [:STUNSPORE,:SLEEPPOWDER].zip([:PARALYSIS,:SLEEP]).each do |id,status|
      target.status=:NONE;target.statusCount=0
      m=move.call(id)
      raise 'status failed' if m.pbFailsAgainstTarget?(user,target,false)
      m.pbEffectAgainstTarget(user,target)
      raise 'status absent' unless target.status==status
    end
    user.hp=5;user.status=:POISON
    move.call(:LIFEDEW).pbEffectAgainstTarget(user,user)
    raise 'Life Dew HP/status' unless user.hp==5+user.totalhp/4 && user.status==:POISON
    move.call(:WISH).pbEffectGeneral(user)
    amount=positions[user.index].effects[PBEffects::WishAmount]
    pbEORWishHealing
    pbRecallAndReplace(user.index,1)
    ally=@battlers[0];before=ally.hp
    pbEORWishHealing
    raise 'Wish switched ally HP/status' unless ally.hp==[before+amount,ally.totalhp].min && ally.status==:POISON
    File.write('FROSTCOON_SUPPORT_PASS.txt','PASS: native PBS; status-only learnset/tutors; revision0/1 save migration; selected support/PP retained; attacks replaced without PP refill; HP/status/identity/item preserved; party/storage/souls/memorials; idempotence; native level10 evolution removes attacks; native Spikes/StickyWeb/Rain/Hail/AuroraVeil gate/paralysis/sleep; LifeDew HP without poison cure; Wish heals switched teammate without poison cure.')
    exit
  rescue Exception => e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('FROSTCOON_SUPPORT_FAIL.txt',e.full_message);exit(1)
  end
end
Battle.prepend(FrostSupportBattle)
