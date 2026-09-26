$player = Player.new("Ren", :POKEMONTRAINER_Red)
$player.character_ID = 1
$game_temp = Struct.new(:in_battle, :in_storage, :regional_dexes_data).new(false, false, nil)
$game_map = Struct.new(:map_id).new(108)
%i[EKANS ARBOK].each do |id|
  ordinary = Pokemon.new(id, 50, $player)
  saved_ordinary = Marshal.dump(ordinary)
  wild = Pokemon.new(id, 5, $player)
  EventHandlers.trigger(:on_wild_pokemon_created, wild)
  raise "wrong form/types" unless wild.form_simple == 1 && wild.types == %i[NORMAL DARK]
  raise "wild poison move" if wild.moves.any? { |m| m.type == :POISON }
  data = wild.species_data
  pool = data.moves.map { |lv, m| m } + data.tutor_moves + data.get_egg_moves
  raise "Poison learnset" if pool.any? { |m| GameData::Move.get(m).type == :POISON }
  base = GameData::Species.get(id)
  unless data.base_stats == base.base_stats && data.abilities == base.abilities &&
           data.hidden_abilities == base.hidden_abilities
    raise "stats/abilities changed"
  end
  unless Marshal.dump(ordinary) == saved_ordinary && ordinary.types == [:POISON]
    raise "ordinary companion changed"
  end
  wild.item = :ORANBERRY
  wild.hp = 1
  wild.status = :PARALYSIS
  wild.moves.first.pp = 0
  before = [
    wild.personalID,
    wild.owner.id,
    wild.item_id,
    wild.hp,
    wild.status,
    wild.moves.map { |m| [m.id, m.pp] }
  ]
  restored = Marshal.load(Marshal.dump(wild))
  raise "save changed form" unless restored.form_simple == 1
  after = [
    restored.personalID,
    restored.owner.id,
    restored.item_id,
    restored.hp,
    restored.status,
    restored.moves.map { |m| [m.id, m.pp] }
  ]
  raise "save changed companion" unless before == after
end
snake = Pokemon.new(:EKANS, 21, $player)
EventHandlers.trigger(:on_wild_pokemon_created, snake)
raise "early evolution" unless snake.check_evolution_on_level_up.nil?
snake.level = 22
raise "missing level22 evolution" unless snake.check_evolution_on_level_up == :ARBOK
snake.species = :ARBOK
raise "lost evolved form" unless snake.form_simple == 1 && snake.types == %i[NORMAL DARK]
if snake.species_data.get_egg_moves.any? { |m| GameData::Move.get(m).type == :POISON }
  raise "poison egg inheritance"
end
$game_map.map_id = 103
foreign = Pokemon.new(:EKANS, 5, $player)
EventHandlers.trigger(:on_wild_pokemon_created, foreign)
raise "unrelated maps changed" unless foreign.form_simple == 0
$game_map.map_id = 108
other = Pokemon.new(:AIPOM, 5, $player)
EventHandlers.trigger(:on_wild_pokemon_created, other)
raise "unrelated species changed" unless other.form_simple == 0
puts "PASS: actual Essentials objects; wild forms/moves, level22 evolution, inherited egg moves, unchanged stats/abilities/ordinary forms, and save roundtrip."
$stdout.flush
$stderr.flush
