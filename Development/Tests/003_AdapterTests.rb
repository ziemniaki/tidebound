def reset_adapter
  $tidebound = Tidebound::State.new
  $tidebound.checkpoint = [10, 5, 6, 2]
  $player = TestPlayer.new([Pokemon.new(:NATU), Pokemon.new(:LAPRAS)])
  $game_map = Struct.new(:map_id).new(10)
  $game_player = Struct.new(:x, :y).new(5, 6)
  WildBattle.outcome, WildBattle.crash, WildBattle.capture_mismatch = 2, false, false
  Tidebound.battle_context = nil
end

T.test("adapter bypasses defeat auto-heal and transfers ownership to spirit records") do
  reset_adapter
  T.equal(:astral, Tidebound.wild!(:ZUBAT, 5))
  T.equal([], $player.party)
  T.equal([0, 0], Tidebound.state.souls.map { |s| s.pokemon.hp })
  T.equal([10, 5, 6], Tidebound.state.souls[0].location.values)
  T.equal(nil, Tidebound.battle_context)
end

T.test("adapter winning battle leaves party in living world") do
  reset_adapter
  WildBattle.outcome = 1
  T.equal(1, Tidebound.wild!(:ZUBAT, 5))
  T.equal(2, $player.party.length)
  T.equal(:living, Tidebound.state.realm)
end

T.test("captured engine copy is not stored or allowed to overwrite original identity") do
  reset_adapter
  Tidebound.wild!(:ZUBAT, 5)
  Tidebound.borrow_guide!
  id = Tidebound.state.waiting_ids.first
  WildBattle.outcome = 4
  T.equal(:recovered, Tidebound.recover_spirit!(id))
  recovered = $player.party.find { |p| Tidebound.identity(p) == id }
  T.equal("Moss", recovered.name)
  T.equal("Keeper", recovered.owner[:name])
  T.equal(:MYSTICSABRE, recovered.item)
  T.equal(2, $player.party.length)
end

T.test("failed encounter archives one companion and keeps other spirits searchable") do
  reset_adapter
  Tidebound.wild!(:ZUBAT, 5)
  Tidebound.borrow_guide!
  id = Tidebound.state.waiting_ids.first
  WildBattle.outcome = 3
  T.equal(:lost, Tidebound.recover_spirit!(id))
  T.equal(1, Tidebound.state.memorials.length)
  T.equal(1, Tidebound.state.waiting_ids.length)
end

T.test("technical battle fault restores party and does not consume the spirit") do
  reset_adapter
  Tidebound.wild!(:ZUBAT, 5)
  Tidebound.borrow_guide!
  id = Tidebound.state.waiting_ids.first
  WildBattle.crash = true
  T.raises(RuntimeError) { Tidebound.recover_spirit!(id) }
  T.equal(:waiting, Tidebound.state.soul(id).status)
  T.equal(40, $player.party[0].hp)
  T.equal(nil, Tidebound.battle_context)
end

T.test("all six original companions can return without exceeding party capacity") do
  reset_adapter
  $player.party = Array.new(6) { Pokemon.new(:NATU) }
  Tidebound.wild!(:ZUBAT, 5)
  Tidebound.borrow_guide!
  WildBattle.outcome = 4
  Tidebound.state.waiting_ids.each { |id| Tidebound.recover_spirit!(id) }
  T.equal(6, $player.party.length)
  T.equal(false, $player.party.any? { |p| Tidebound.borrowed?(p) })
end

T.test("zero survivors still permit a return, with a new low-HP companion") do
  reset_adapter
  Tidebound.state.checkpoint = [20, 2, 2, 2]
  Tidebound.wild!(:ZUBAT, 5)
  Tidebound.borrow_guide!
  T.equal([20, 2, 2, 2], Tidebound.return_to_living!)
  T.equal(:living, Tidebound.state.realm)
  T.equal(2, Tidebound.state.memorials.length)
  T.equal(1, $player.party.length)
  T.equal(10, $player.party[0].hp)
  T.assert(!Tidebound.borrowed?($player.party[0]))
end

T.test("ordinary catches remain on the normal engine storage path") do
  reset_adapter
  battle = Battle.new
  pkmn = Pokemon.new(:NATU)
  battle.pbStorePokemon(pkmn)
  T.equal([pkmn], battle.stored)
end

T.test("spirit catch rate override leaves ordinary species rates intact") do
  reset_adapter
  battle = Battle.new
  Tidebound.battle_context = :spirit
  battle.pbCaptureCalc(nil, nil, 200, :POKEBALL)
  T.equal(35, battle.received_rate)
  Tidebound.battle_context = nil
  battle.pbCaptureCalc(nil, nil, 200, :POKEBALL)
  T.equal(200, battle.received_rate)
end

T.test("six-turn spirit deadline ends only unresolved spirit battles") do
  reset_adapter
  battle = Battle.new
  Tidebound.battle_context = :spirit
  5.times { battle.pbEndOfRoundPhase }
  T.equal(0, battle.decision)
  battle.pbEndOfRoundPhase
  T.equal(3, battle.decision)
  T.equal(1, battle.messages.length)
  Tidebound.battle_context = nil
  normal = Battle.new
  10.times { normal.pbEndOfRoundPhase }
  T.equal(0, normal.decision)
end

T.test("SaveData registration resets new games and serializes complete custom state") do
  reset_adapter
  Tidebound.wild!(:ZUBAT, 5)
  registry = SaveData.value(:tidebound)
  stored = Marshal.load(Marshal.dump(registry.save_proc.call))
  $tidebound = nil
  registry.load_proc.call(stored)
  T.equal(:astral, Tidebound.state.realm)
  T.equal(2, Tidebound.state.souls.length)
  T.equal(true, registry.reset)
  registry.load_proc.call(registry.new_proc.call)
  T.equal(:living, Tidebound.state.realm)
  T.equal([], Tidebound.state.memorials)
end

T.test("mismatched capture is a technical fault, not a permanent companion loss") do
  reset_adapter
  Tidebound.wild!(:ZUBAT, 5)
  Tidebound.borrow_guide!
  id = Tidebound.state.waiting_ids.first
  WildBattle.outcome, WildBattle.capture_mismatch = 4, true
  T.raises(Tidebound::TransitionError) { Tidebound.recover_spirit!(id) }
  T.equal(:waiting, Tidebound.state.soul(id).status)
  T.equal(0, Tidebound.state.memorials.length)
end

T.test("battle without a return checkpoint is rejected without harming the party") do
  reset_adapter
  Tidebound.state.checkpoint = nil
  T.raises(Tidebound::TransitionError) { Tidebound.wild!(:ZUBAT, 5) }
  T.equal(:living, Tidebound.state.realm)
  T.equal(2, $player.party.length)
end

TestSuite.finish
