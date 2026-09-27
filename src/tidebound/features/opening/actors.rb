# Household availability belongs to the opening, including its walking/dream states.
Tidebound::Actors.on_frame("house", "room", "outside_dog") do |event, actor|
  species = actor.fetch("species").to_sym
  next false unless (Tidebound.story[:household_pets] || {})[species]
  walk = Tidebound.story[:walk_state]
  if actor["role"] == "outside_dog"
    %i[not_started requested running at_pier].include?(walk)
  elsif actor["role"] == "room" && species == :NATU
    next false if walk == :complete
    event.map_id != Tidebound::World::MAPS[:dream] || Tidebound::DreamRoom.wick_visible?
  else
    species == :MAKUHITA || walk == :complete
  end
end
Tidebound::Actors.on_frame("keys") do |_event, _actor|
  !Tidebound.story[:keys_collected] && !Tidebound.story[:shop_unlocked]
end
Tidebound::Actors.on_frame("crate") { |_event, _actor| true }
Tidebound::Actors.on_frame("wood_bird") { |_event, _actor| !Tidebound.story[:wood_bird_gone] }
