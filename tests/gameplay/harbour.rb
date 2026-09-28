# Optional harbour errands compose with the real bag/save codec and battle adapter.
h = Tidebound::Harbour
r = Tidebound::DockRing
new_opening
Tidebound::World.travel(:docks, 11, 28)
$quest_reject_item = h::LETTER
h.courier
check(!$bag.has?(h::LETTER) && !h.flags[:letter_started], "full bag consumed letter")
$quest_reject_item = nil
h.courier
h.courier
check($bag.quantity(h::LETTER) == 1, "letter duplicated")
roundtrip
h.resident
check(h.flags[:letter_delivered] && !$bag.has?(h::LETTER), "letter delivery lost")
$quest_reject_item = :ORANBERRY
h.courier
check(!h.flags[:letter_paid], "undelivered letter reward marked paid")
$quest_reject_item = nil
2.times { h.courier }
check($bag.quantity(:ORANBERRY) == 2, "letter reward missing or duplicated")
h.nets
check(!$bag.has?(h::SHUTTLE), "unrequested shuttle taken")
h.mender
$quest_reject_item = h::SHUTTLE
h.nets
check(!$bag.has?(h::SHUTTLE), "shuttle pickup bypassed bag capacity")
$quest_reject_item = nil
h.nets
roundtrip
$quest_reject_item = :SILKSCARF
h.mender
check(h.flags[:shuttle_returned] && !h.flags[:shuttle_paid], "shuttle reward cannot retry")
$quest_reject_item = nil
2.times { h.mender }
check($bag.quantity(:SILKSCARF) == 1 && !$bag.has?(h::SHUTTLE), "shuttle reward duplicated")
h.porter
h.cargo(:west)
h.cargo(:middle)
h.porter
check(!h.flags[:oil_missing], "cargo quest skipped uninspected lot")
h.cargo(:east)
$choices = [0]
h.porter
check(!h.flags[:oil_missing], "wrong answer completed count")
$choices = [1]
h.porter
check(h.flags[:oil_missing], "correct count not accepted")
roundtrip
h.harker
check(h.flags[:oil_returned] && !r.flags[:offer], "oil return unexpectedly started a battle")
$quest_reject_item = :ORANBERRY
h.porter
check(!h.flags[:cargo_paid], "cargo reward lost on full bag")
$quest_reject_item = nil
2.times { h.porter }
check($bag.quantity(:ORANBERRY) == 5, "cargo reward duplicated")
check(!Tidebound::DemoLaunch.flags[:completed], "optional jobs completed the main demo")
puts "PASS: harbour delivery/counting quests survive saves, wrong answers and full bags without duplicate rewards."

new_opening
$player.party = [Pokemon.new(:NATU, 12), Pokemon.new(:MAKUHITA, 14)]
$player.party.first.item = :MYSTICWATER
$player.pokedex.set_seen(:NATU)
$player.pokedex.set_seen(:MEWTWO)
before = Marshal.dump($player.party)
offer = r.offer
check(
  offer[:team].length == 2 && offer[:team].all? { |_id, level| (10..12).include?(level) },
  "ring levels/size"
)
check(Marshal.dump($player.party) == before, "ring generation modified player companions")
saved = Marshal.dump(offer)
roundtrip
check(Marshal.dump(r.offer) == saved, "save rerolled the offer")
$choices = [false]
r.challenge
check(!r.offer[:used] && Marshal.dump(r.offer) == saved, "declining consumes/rerolls offer")
$quest_outcome = 0
r.challenge
check(!r.offer[:used] && !r.flags[:wins], "aborted battle consumes offer or counts win")
$quest_outcome = 1
r.challenge
check(r.offer[:used] && r.flags[:wins] == 1, "completed battle not recorded")
r.challenge
check(r.flags[:wins] == 1, "same offer can be farmed")
expiry = r.offer[:expires_at]
check(r.offer(expiry - 1)[:used], "offer renewed early")
check(!r.offer(expiry)[:used], "offer did not renew at expiry")
expiry = r.offer[:expires_at]
$player.party = [Pokemon.new(:NATU, 1)]
rebalance = r.offer
check(rebalance[:team].length == 1 && rebalance[:team][0][1] == 1, "level-one party not supported")
check(rebalance[:expires_at] == expiry, "party change resets cooldown")
$player.party.first.hp = 0
check(r.offer.nil?, "unable party gets a challenger")

# Deterministically cover all 100 bucket draws: 80 familiar, 20 unfamiliar.
class RingDraws
  def initialize(bucket)
    @values = [0, bucket, 0]
  end
  def rand(limit)
    value = @values.shift
    raise "Unexpected ring RNG call" unless value && value < limit
    value
  end
end
seen_count =
  (0...100).count do |bucket|
    species = r.generate_team([20], RingDraws.new(bucket))[0][0]
    $player.pokedex.seen?(species)
  end
check(seen_count == 80, "familiar/unfamiliar selection is not 80/20 with both pools present")
[1, 5, 15, 35, 70, 100].each do |level|
  12.times do |seed|
    team = r.generate_team([level] * 6, Random.new(seed))
    check(team.length == 3 && team.map(&:first).uniq.length == 3, "invalid/duplicate ring team")
    team.each do |id, actual|
      data = GameData::Species.get(id)
      check(
        actual.between?([level - 3, 1].max, [level - 1, 1].max),
        "opponent not just below party"
      )
      check(data.minimum_level <= actual, "underlevel evolution")
      check(
        data.base_stat_total < 600 && !data.has_flag?("Legendary") && !data.has_flag?("Mythical"),
        "forbidden ring species"
      )
    end
  end
end

[2, 5].each do |outcome|
  new_opening
  $player.party = [Pokemon.new(:NATU, 12)]
  $quest_outcome = outcome
  Tidebound::World.travel(:docks, 69, 27)
  current = r.offer
  r.challenge
  check(current[:used] && !r.flags[:wins], "loss/draw recorded as win or left reusable")
  check(
    Tidebound.state.realm == :astral && $game_map.map_id == 105,
    "ring defeat bypassed astral transfer"
  )
  roundtrip
  check(r.flags[:offer][:used], "ring defeat cooldown lost after saving")
end
puts "PASS: ring generation, 80/20 pools, cooldown, save continuity, cancellation and real loss/draw recovery."
