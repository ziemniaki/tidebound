Tidebound::Actors.on_entry(:road_thief) do |_event, _actor|
  Tidebound::NeighborQuest.stage == :pursuit && !Tidebound::NeighborQuest.q[:first_won]
end
Tidebound::Actors.on_entry(
  :running_thief,
  :robbery_youth_one,
  :robbery_youth_two
) { |_event, _actor| false }
Tidebound::Actors.on_frame("neighbor_wild") do |_event, actor|
  Tidebound::NeighborQuest.wild_visible?(actor.fetch("state").to_sym)
end
