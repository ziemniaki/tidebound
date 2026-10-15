# The existing native storage backend, using the real Essentials save codec.
SaveData.register(:storage_system) do
  ensure_class :PokemonStorage
  save_value { $PokemonStorage }
  load_value { |value| $PokemonStorage = value }
end
new_opening
s = Tidebound::Sanctuary
$PokemonStorage = PokemonStorage.new
$player.party = 6.times.map { |i| Pokemon.new(:NATU, 12 + i) }
$player.party.each { |pet| Tidebound.state.assign_identity(pet) }
seventh = Pokemon.new(:AIPOM, 14)
seventh.name = "Seventh"
seventh.item = :SILKSCARF
Tidebound.state.assign_identity(seventh)
seventh_id = Tidebound.identity(seventh)
check($PokemonStorage.pbStoreCaught(seventh) == 0, "native seventh catch was not stored")
check(!s.withdraw(0, 0), "withdraw overflowed full party")
first = $player.party[0]
first.hp = 3
first.status = :POISON
first.moves.first.pp = 1
first.item = :MYSTICWATER
first_saved = Marshal.dump(first)
check(s.exchange(0, 0, 0), "full-party exchange failed")
check(
  $player.party.first.equal?(seventh) && $PokemonStorage[0, 0].equal?(first),
  "exchange replaced individuals"
)
check(Marshal.dump($PokemonStorage[0, 0]) == first_saved, "resting healed or changed a companion")
roundtrip
check(
  Tidebound.identity($player.party.first) == seventh_id &&
    $player.party.first.item_id == :SILKSCARF,
  "saved sanctuary lost identity/item"
)
check(Marshal.dump($PokemonStorage[0, 0]) == first_saved, "saved storage changed injured companion")
check(s.deposit(1) && $player.party.length == 5, "deposit failed")
check(s.withdraw(0, 0) && $player.party.length == 6, "withdraw failed")
check(
  Marshal.dump($player.party.last) == first_saved,
  "withdraw lost injuries, PP, moves or held item"
)

$player.party = [$player.party.first]
$PokemonStorage = PokemonStorage.new(1, 1)
check(!s.deposit(0) && $player.party.length == 1, "last able companion can be deposited")
fainted = Pokemon.new(:NATU, 12)
fainted.hp = 0
$PokemonStorage[0, 0] = fainted
check(
  !s.exchange(0, 0, 0) && $player.party.first.hp > 0,
  "exchange stranded player without an able companion"
)
$player.party << Pokemon.new(:AIPOM, 12)
party = Marshal.dump($player.party)
check(!s.deposit(0) && Marshal.dump($player.party) == party, "full refuge lost outgoing companion")
check(!s.withdraw(99, 0) && !s.exchange(0, 99, 0), "invalid storage coordinates accepted")

$PokemonStorage = PokemonStorage.new(1, 12)
12.times { |i| $PokemonStorage[0, i] = Pokemon.new(:AIPOM, i + 1) }
$choices = [10, 1]
selected = s.choose_stored
check(selected[0..1] == [0, 11], "paged sanctuary selected wrong individual")
$choices = [-1]
check(s.choose_stored.nil?, "cancelled selection returned a companion")
$choices = [3]
s.open
SaveData.unregister(:storage_system)
puts "PASS: seventh catch retrieval, full-party swaps, storage save roundtrip, unchanged injuries/items/identity, last-companion/full-refuge safeguards and paged cancellation."
