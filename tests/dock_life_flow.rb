# Real species, bags, party objects and save codec; UI and battle outcomes mocked.
d = Tidebound::DockLife
r = Tidebound::QuayRing
new_opening
$player.party = [Pokemon.new(:NATU, 12), Pokemon.new(:MAKUHITA, 10)]
Tidebound::World.travel(:docks, 21, 28)
d.canvas
check(!$bag.has?(:TBDOCKCANVAS), "canvas taken before request")
d.sailmaker
d.canvas
roundtrip
d.sailmaker
d.sailmaker
check($bag.quantity(:SILKSCARF) == 1 && !$bag.has?(:TBDOCKCANVAS), "sail reward duplicated")
$choices = [true]
d.courier
roundtrip
d.tomas
d.tomas
check($bag.quantity(:ORANBERRY) == 3 && !$bag.has?(:TBDOCKLETTER), "letter reward/delivery")
$choices = [true]
d.cook
d.netmender
d.netmender
roundtrip
d.tomas
d.lamplighter
$quest_reject_item = :SITRUSBERRY
d.cook
check(!d.state[:meal_paid] && $bag.has?(:TBDOCKMEALS), "full bag loses reward")
$quest_reject_item = nil
d.cook
d.cook
check($bag.quantity(:SITRUSBERRY) == 2 && !$bag.has?(:TBDOCKMEALS), "meal rewards repeat")
check(d.state[:meals].sort == %i[lio sen tomas], "meal duplicated")
puts "PASS: three dock errands, save roundtrips, full-bag reward retries, no duplication."

# Use the complete real species database for eligibility tests (art is native-tested).
entries = []
GameData::Species.each { |data| entries << data }
$player.pokedex.set_seen(:RATTATA)
$player.pokedex.set_seen(:PIDGEY)
$player.pokedex.set_seen(:NATU)
rng = Random.new(7351)
seen_count = 0
1000.times do
  row = r.roster([$player.party.first], $player.pokedex, rng, entries).first
  data = GameData::Species.get_species_form(row[0], row[1])
  check(row[2].between?(9, 11), "ring level out of range")
  check(r.eligible?(data, row[2]), "unsuitable ring species")
  seen_count += 1 if $player.pokedex.seen?(row[0])
end
check(seen_count.between?(750, 850), "seen preference diverges from 80%: #{seen_count}")
%i[MEWTWO ARTICUNO MEW DRATINI DRAGONITE LARVITAR DEINO NIVALORA FROSTCOON].each do |species|
  check(!r.eligible?(GameData::Species.get(species), 100), "forbidden ring species #{species}")
end
[1, 5, 15, 25, 55, 100].each do |level|
  team = r.roster([Pokemon.new(:NATU, level)], $player.pokedex, rng, entries)
  check(team.length == 1 && team[0][2] <= [1, level - 1].max, "party scaling #{level}")
  trainer = r.challenger({ name: "Test", team: team })
  check(trainer.party.first.moves.any? { |m| m.power > 0 }, "no damage-capable moves")
end
puts "PASS: generated levels, actual legal moves, exceptional-family bans; #{seen_count}/1000 seen picks."

# A declined/cancelled ticket persists; only a resolved battle consumes the interval.
r.state[:offer] = { name: "Bram", team: [[:RATTATA, 0, 9]] }
$choices = [false]
r.talk
roundtrip
check(r.state[:offer][:name] == "Bram" && r.remaining == 0, "decline consumes/rerolls")
$quest_outcome = 0
$choices = [true]
r.talk
check(r.remaining == 0 && r.state[:offer], "aborted battle consumed interval")
$quest_outcome = 1
$choices = [true]
money = $player.money
r.talk
check(r.state[:wins] == 1 && $player.money == money + 105, "win purse")
roundtrip
check(r.remaining > 895 && !r.state[:offer], "cooldown not saved")
r.talk
check(r.state[:wins] == 1 && $player.money == money + 105, "cooldown allows repeat")
t = r.state[:last_battle]
check(r.remaining(t + 899) == 1 && r.remaining(t + 900) == 0, "quarter-hour boundary")
check(r.remaining(t - 100) == 900, "backward clock exceeds cooldown")
r.state[:last_battle] = Time.now.to_i - 901
r.state[:offer] = { name: "Della", team: [[:RATTATA, 0, 9]] }
$quest_outcome = 2
$choices = [true]
r.talk
check(Tidebound.state.realm == :astral && r.remaining > 895, "loss bypasses death/cooldown")
check(r.state[:wins] == 1 && $player.money == money + 105, "loss rewarded")
puts "PASS: decline, cancellation, save-persistent cooldown, win purse, loss/astral behavior."
