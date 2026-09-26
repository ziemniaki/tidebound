T = TestSuite

def fresh_state
  Tidebound::State.new
end

def fallen_pair(state)
  pair = [Pokemon.new(:NATU), Pokemon.new(:LAPRAS)]
  pair.each { |p| p.hp = 0 }
  ids = state.enter_astral!(pair, {:map_id => 11, :x => 4, :y => 8})
  [pair, ids]
end

T.test("death snapshots the individual and detaches mutable data") do
  state = fresh_state
  pair, ids = fallen_pair(state)
  pair[0].moves[0].pp = 99
  pair[0].owner[:name] = "Changed"
  T.equal(:astral, state.realm)
  T.equal(7, state.soul(ids[0]).pokemon.moves[0].pp)
  T.equal("Keeper", state.soul(ids[0]).pokemon.owner[:name])
end

T.test("recapture preserves name, owner, IVs, EVs, moves, form and item") do
  state = fresh_state
  pair, ids = fallen_pair(state)
  foe = state.begin_encounter!(ids[0])
  foe.name, foe.owner, foe.form = "Impostor", {}, 9
  restored = state.recover!(ids[0])
  [:name, :owner, :iv, :ev, :personalID, :form, :item].each do |field|
    T.equal(pair[0].public_send(field), restored.public_send(field))
  end
  T.equal(ids[0], Tidebound.identity(restored))
  T.equal(10, restored.hp)
  T.equal(7, restored.moves[0].pp)
end

T.test("spirit opponent is healthy and carries no duplicable item") do
  state = fresh_state
  _, ids = fallen_pair(state)
  foe = state.begin_encounter!(ids[0])
  T.equal(40, foe.hp)
  T.equal(nil, foe.item)
  T.equal(:MYSTICSABRE, state.soul(ids[0]).pokemon.item)
end

T.test("encounter is spent after permanent loss and cannot be replayed") do
  state = fresh_state
  _, ids = fallen_pair(state)
  state.begin_encounter!(ids[0])
  state.lose!(ids[0], :encounter_failed)
  T.raises(Tidebound::TransitionError) { state.begin_encounter!(ids[0]) }
  T.raises(Tidebound::TransitionError) { state.recover!(ids[0]) }
  T.raises(Tidebound::TransitionError) { state.lose!(ids[0]) }
  T.equal(1, state.memorials.length)
end

T.test("one encounter cannot overlap another") do
  state = fresh_state
  _, ids = fallen_pair(state)
  state.begin_encounter!(ids[0])
  T.raises(Tidebound::TransitionError) { state.begin_encounter!(ids[1]) }
  T.raises(Tidebound::TransitionError) { state.leave_astral! }
end

T.test("leaving marks waiting spirits lost with recorded location") do
  state = fresh_state
  fallen_pair(state)
  state.leave_astral!
  T.equal(:living, state.realm)
  T.equal(2, state.memorials.length)
  T.equal(:left_behind, state.memorials[0].reason)
  T.equal(11, state.memorials[0].location[:map_id])
end

T.test("same companion can survive one death and be lost on the next") do
  state = fresh_state
  _, ids = fallen_pair(state)
  state.begin_encounter!(ids[0])
  survivor = state.recover!(ids[0])
  state.leave_astral!
  state.enter_astral!([survivor], {:map_id => 12})
  T.equal([ids[0]], state.waiting_ids)
  state.lose!(ids[0])
  T.equal(2, state.memorials.length)
end

T.test("lost identities cannot be reintroduced and duplicated") do
  state = fresh_state
  pair, ids = fallen_pair(state)
  state.leave_astral!
  T.raises(Tidebound::TransitionError) { state.enter_astral!([pair[0]], {}) }
  T.equal(:living, state.realm)
end

T.test("duplicate party identities are rejected before astral transition") do
  state = fresh_state
  pkmn = Pokemon.new(:NATU)
  state.assign_identity(pkmn)
  T.raises(Tidebound::TransitionError) { state.enter_astral!([pkmn, Tidebound.copy(pkmn)], {}) }
  T.equal(:living, state.realm)
end

T.test("nested death, empty parties and eggs are rejected") do
  state = fresh_state
  T.raises(Tidebound::TransitionError) { state.enter_astral!([], {}) }
  egg = Pokemon.new(:NATU); egg.egg = true
  T.raises(Tidebound::TransitionError) { state.enter_astral!([egg], {}) }
  pair, _ = fallen_pair(state)
  T.raises(Tidebound::TransitionError) { state.enter_astral!(pair, {}) }
end

T.test("rest gives an HP and PP floor without curing poison or cumulative healing") do
  state = fresh_state
  pkmn = Pokemon.new(:NATU)
  pkmn.hp, pkmn.status = 1, :POISON
  10.times { state.rest!([pkmn]) }
  T.equal(10, pkmn.hp)
  T.equal(:POISON, pkmn.status)
  T.equal(1, pkmn.moves[1].pp)
  T.equal(7, pkmn.moves[0].pp)
  pkmn.hp = 30
  state.rest!([pkmn])
  T.equal(30, pkmn.hp)
end

T.test("cemetery uses exact lost companions, fills vacancies and preserves archives") do
  state = fresh_state
  _, ids = fallen_pair(state)
  state.leave_astral!
  backup = Array.new(6) { Pokemon.new(:XATU, 50) }
  team = state.cemetery_team(backup)
  T.equal(6, team.length)
  T.equal([:NATU, :LAPRAS, :XATU, :XATU, :XATU, :XATU], team.map(&:species))
  T.equal(ids[0], Tidebound.identity(team[0]))
  T.equal(0, state.memorials[0].pokemon.hp)
  team[0].moves[0].pp = 2
  T.equal(7, state.memorials[0].pokemon.moves[0].pp)
end

T.test("no-loss cemetery uses complete fallback, inadequate fallback fails clearly") do
  state = fresh_state
  team = state.cemetery_team(Array.new(6) { Pokemon.new(:XATU) })
  T.equal(6, team.length)
  T.raises(ArgumentError) { state.cemetery_team([]) }
end

T.test("cemetery uses the six most recent losses without exceeding team size") do
  state = fresh_state
  4.times do
    fallen_pair(state)
    state.leave_astral!
  end
  T.equal(8, state.memorials.length)
  T.equal(6, state.cemetery_team([]).length)
end

T.test("save round trip preserves identities, encounter states, archive and checkpoint") do
  state = fresh_state
  state.checkpoint = [2, 3, 4, 2]
  _, ids = fallen_pair(state)
  state.lose!(ids[0])
  loaded = Marshal.load(Marshal.dump(state))
  T.equal(:astral, loaded.realm)
  T.equal([ids[1]], loaded.waiting_ids)
  T.equal([2, 3, 4, 2], loaded.checkpoint)
  T.equal(ids[0], loaded.memorials[0].id)
  loaded.begin_encounter!(ids[1])
  T.equal(ids[1], Tidebound.identity(loaded.recover!(ids[1])))
end

T.test("victory without healed Suicune stays dark") do
  state = fresh_state
  state.resolve_suicune!(:corrupted)
  state.resolve_suicune!(:killed)
  state.story[:mystic_sabre] = true
  state.story[:final_demon_defeated] = true
  T.equal(:dark_victory, state.ending)
  T.raises(Tidebound::TransitionError) { state.resolve_suicune!(:healed) }
end

T.test("healing, sabre and final victory are all needed for restoration") do
  state = fresh_state
  state.resolve_suicune!(:corrupted)
  state.resolve_suicune!(:rescued)
  state.resolve_suicune!(:healed)
  T.equal(:unfinished, state.ending)
  state.story[:final_demon_defeated] = true
  T.equal(:dark_victory, state.ending)
  state.story[:mystic_sabre] = true
  T.equal(:restoration, state.ending)
  state.resolve_suicune!(:lost)
  T.equal(:dark_victory, state.ending)
end

