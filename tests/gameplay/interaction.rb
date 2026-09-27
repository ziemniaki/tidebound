# Exercise the final shared-NPC dispatch rather than a prepend chain.
new_opening
n = Tidebound::NeighborQuest
v = Tidebound::VaultVisit
i = Tidebound::Interactions
n.q[:stage] = :complete
Tidebound::World.travel(:shop, 8, 10)
i.oil_seller
check(v.q[:gift] && $bag.quantity(v::GIFT) == 1, "vault reward missing")
i.oil_seller
check($bag.quantity(v::GIFT) == 1, "vault reward repeated")
Tidebound::World.travel(:home, 10, 12)
i.mother
check(v.q[:open], "mother did not open vault after the gift")
v.q[:museum] = true
i.mother
check($messages.last.include?("Did you find the museum?"), "museum dialogue lost precedence")
check(i.hint == v.hint, "journal does not prefer the current chapter")
puts "PASS: explicit shared-NPC dispatch, unique vault gift, mother and journal chapter precedence."
