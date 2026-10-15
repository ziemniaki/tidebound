# Full production composition; only the animated front end is doubled here.
module Tidebound::CastawayVoyage
  class << self
    alias native_play play
    def play(**options)
      raise "Interrupted crossing" if $castaway_interrupt
      ($castaway_voyages ||= []) << options
    end
  end
end

c = Tidebound::Castaway
new_opening
$player.party = [Pokemon.new(:NATU, 15), Pokemon.new(:MAKUHITA, 14)]
$player.party.first.item = :MYSTICWATER
before = Marshal.dump([$player.party, $bag])
Tidebound::World.travel(:docks, :captain)
$choices = [false]
Tidebound::DemoLaunch.voyage
check($game_map.map_id == 112 && !c.flags[:arrived], "cancelled voyage left harbour")
$castaway_interrupt = true
begin
  c.depart
  raise "Expected interrupted crossing"
rescue RuntimeError => error
  raise unless error.message == "Interrupted crossing"
ensure
  $castaway_interrupt = false
end
check($game_map.map_id == 112 && !c.flags[:arrived], "interrupted voyage committed arrival")
c.depart
c.arrival
check($game_map.map_id == 119 && c.flags[:greeted], "captain did not enter the island")
check(Marshal.dump([$player.party, $bag]) == before, "wreck changed companions or belongings")
check(Tidebound.state.checkpoint.first == 119, "wreck retained mainland recovery point")
roundtrip
c.arrival
check(c.flags[:greeted], "island arrival did not survive save")

Tidebound::World.travel(:fruit_canopy, :garden)
c.garden_path
check($game_map.map_id == 121, "troop gate can be bypassed")
c.troop
check(!c.flags[:troop], "troop accepted player before water")
Tidebound::World.travel(:freshwater_hollow, :canopy)
$choices = [0]
c.spring
check(!c.flags[:water], "wrong channel solved spring")
$choices = [3]
c.spring
check(!c.flags[:water], "cancelled spring solved puzzle")
$choices = [2]
c.spring
roundtrip
check(c.flags[:water], "spring restoration lost after save")
Tidebound::World.travel(:fruit_canopy, :garden)
c.fruit
$choices = [true, 0]
c.troop
check(!c.flags[:troop] && c.flags[:fruit], "wrong pass advanced or consumed unique fruit")
$choices = [true, 1, 3]
c.troop
check(!c.flags[:troop], "cancelled passing game advanced")
$choices = [true, 1, 0, 2]
c.troop
c.garden_path
check($game_map.map_id == 123 && c.flags[:troop], "correct passing game did not open garden")
roundtrip
c.salvage(:tools)
Tidebound::World.travel(:wreck_beach, :camp)
c.captain
check(!c.flags[:repaired], "hull repaired without shelter")
$choices = [false]
c.salvage(:canvas)
check(!c.flags[:canvas], "cancelled salvage delivered canvas")
c.salvage(:canvas)
$choices = [3]
c.nell
c.captain
check(c.flags[:shelter] && c.flags[:repaired], "camp and hull failed to advance")
roundtrip
Tidebound::World.travel(:signal_ridge, :signal)
$choices = [false]
c.signal
check(!c.flags[:signalled], "cancelled signal advanced story")
c.signal
check(c.flags[:signalled], "signal failed")
$choices = [false]
c.return_home
check($game_map.map_id == 124 && !c.flags[:completed], "cancelled return abandoned island")
c.return_home
check($game_map.map_id == 112 && c.flags[:completed], "chapter could not return home")
roundtrip
c.depart
check($game_map.map_id == 119 && c.flags[:completed], "completed island cannot be revisited")
check(Marshal.dump([$player.party, $bag]) == before, "chapter changed party or bag unexpectedly")

new_opening
$quest_reject_item = :SUPERPOTION
c.supplies
check(
  c.flags[:balls] && !c.flags[:medicine] && $bag.quantity(:GREATBALL) == 12,
  "partial supplies were not recorded"
)
roundtrip
$quest_reject_item = nil
2.times { c.supplies }
check(
  $bag.quantity(:GREATBALL) == 12 && $bag.quantity(:SUPERPOTION) == 5 && c.flags[:supplies],
  "supply retry duplicated or lost items"
)

module Tidebound::CastawayVoyage
  class << self
    alias play native_play
    remove_method :native_play
  end
end
puts "PASS: voyage cancellation/interruption, intact belongings, water/troop puzzles, partial rewards, camp repairs, signal, save continuity and return visits."
