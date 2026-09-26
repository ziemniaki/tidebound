# TEST ONLY: inject into a disposable engine, never release Scripts.rxdata.
$stdout.sync=true
module PondTestInput
  def trigger?(key)
    return Graphics.frame_count%6==0 if key==Input::USE
    return false if key==Input::BACK
    super
  end
end
Input.singleton_class.prepend(PondTestInput)
class Scene_TideboundTitle
  def main
    $data_system.start_map_id=108;$data_system.start_x=26;$data_system.start_y=54
    Game.start_new;$scene=Scene_Map.new;$player.name='Ren'
    Tidebound::Opening.flags.merge!(opening_started:true,opening_revision:4,coast_revision:5,starter_chosen: :NATU)
    Tidebound::NeighborQuest.q.merge!(stage: :pursuit,first_won:true)
    hero=Pokemon.new(:NATU,45);hero.learn_move(:PSYCHIC);hero.moves=[Pokemon::Move.new(:PSYCHIC)]
    $player.party=[hero];Tidebound.state.checkpoint=[108,26,39,8]
  end
end
module PondNativeCheck
  def shot(name,x,y)
    $game_player.moveto(x,y)
    30.times { Graphics.update;Input.update;updateSpritesets }
    b=Graphics.snap_to_bitmap;b.to_file("pond-#{name}.png");b.dispose
  end
  def update
    super
    return if @pond_test || !$player || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @pond_test=true
    pond=Tidebound::Pond
    duck=$game_map.events.values.find { |e| e.name=='Wild:PSYDUCK:shoreduck' }
    raise 'duck location' unless [duck.x,duck.y]==[19,62]
    shot('north',27,55);shot('west',18,61);shot('south',29,72)
    exit if ENV['TB_POND_VISUAL']=='1'
    grass=[]
    $game_map.height.times { |y| $game_map.width.times { |x| grass<<[x,y] if $game_map.data[x,y,1]==391 } }
    southern=grass.find { |x,y| y>=48 };northern=grass.find { |x,y| y<48 }
    raise 'missing grass zones' unless southern && northern
    $game_player.moveto(*southern)
    raise 'local encounter type' unless $PokemonEncounters.encounter_type==:PondGrass
    rolls=300.times.map { $PokemonEncounters.choose_wild_pokemon(:PondGrass) }
    raise 'pond species' unless rolls.map(&:first).uniq.sort==[:AIPOM,:PSYDUCK,:SUNKERN].sort
    raise 'pond levels' unless rolls.all? { |s,l| (8..11).include?(l) }
    $game_player.moveto(*northern);raise 'road changed' unless $PokemonEncounters.encounter_type==:Land
    x,y=Tidebound::PondGeometry::WATER.first
    raise 'water terrain' unless $game_map.terrain_tag(x,y).can_surf
    raise 'walked on water' if $game_map.passable?(x,y,2,$game_player)
    $PokemonGlobal.surfing=true
    raise 'surf passage' unless $game_map.playerPassable?(x,y,2,$game_player)
    raise 'NPC can swim' if $game_map.passable?(x,y,2,duck)
    $PokemonGlobal.surfing=false
    pond.flags.delete(:revision);$game_player.moveto(x,y);pond.safe_arrival
    raise 'legacy landing' unless [$game_player.x,$game_player.y]==[26,52]
    before=$bag.quantity(:MYSTICWATER);pond.hidden_item;pond.hidden_item
    raise 'cache duplication' unless $bag.quantity(:MYSTICWATER)==before+1 && pond.flags[:cache]
    $game_player.moveto(25,54);pond.fisher(:toma)
    raise 'trainer win not remembered' unless pond.flags[:toma]
    pond.fisher(:toma)
    raise 'save failed' unless Game.save('pond-complete.rxdata')
    File.write('POND_NATIVE_PASS.txt','PASS: rendered pond; moved duck; local encounter selection and levels; north table unchanged; Surf passage; legacy landing; unique item; actual fisherman battle and win persistence; native save.')
    exit
  rescue Exception=>e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('POND_NATIVE_FAIL.txt',e.full_message);puts e.full_message;exit(1)
  end
end
Scene_Map.prepend(PondNativeCheck)
