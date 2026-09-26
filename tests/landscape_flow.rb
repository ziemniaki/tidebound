# Saved players/followers on the old walkable table must be moved safely.
new_opening
$game_map.map_id = 101
$game_map.events = {}
followers = []
$PokemonGlobal.define_singleton_method(:followers) { followers }
$game_temp.define_singleton_method(:followers=) { |value| @followers = value }
$player.party = [Pokemon.new(:NATU, 7, $player)]
before = Marshal.dump([$player.party, $bag])
[8, 9].each do |x|
  check(Tidebound::MAP_PASSAGES[101][7][x] == '0', 'table top is walkable')
  Tidebound::Opening.flags[:landscape_revisions] = {101 => 2, 108 => 2}
  $game_player.moveto(x, 7)
  follower = Struct.new(:current_map_id, :name, :x, :y).new(101, 'Tidebound Pookie', x, 7)
  followers.replace([follower])
  Tidebound::Landscape.safe_arrival
  check(Tidebound::MAP_PASSAGES[101][$game_player.y][$game_player.x] == '1', 'legacy table save is stuck')
  check([follower.x, follower.y] == [$game_player.x, $game_player.y], 'legacy follower is stuck on table')
  position = [$game_player.x, $game_player.y]
  Tidebound::Landscape.safe_arrival
  check(position == [$game_player.x, $game_player.y], 'table migration repeats')
  check(Marshal.dump([$player.party, $bag]) == before, 'table migration changed party or inventory')
end
$game_map.map_id = 108
$game_player.moveto(0, 0)
Tidebound::Landscape.safe_arrival
check([$game_player.x, $game_player.y] == [0, 0], 'unrelated map migration was repeated')
puts 'PASS: solid lighthouse table; old player/follower positions migrate once without changing party or bag.'
