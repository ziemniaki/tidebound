# Shared mother/seller placements follow the visit's public story state.
Tidebound::Actors.on_entry(:seller_outside) { |_event, _actor| !Tidebound.story[:shop_unlocked] }
Tidebound::Actors.on_entry(:mother_visiting) { |_event, _actor| false }
Tidebound::Actors.on_entry(:mother) do |_event, _actor|
  !Tidebound::VaultVisit.q[:open] || Tidebound::VaultVisit.q[:museum]
end
Tidebound::Actors.on_entry(:seller_at_home) do |_event, _actor|
  Tidebound::VaultVisit.q[:gift] && !Tidebound::VaultVisit.q[:open]
end
Tidebound::Actors.on_entry(:oil_seller) do |_event, _actor|
  !Tidebound::VaultVisit.q[:gift] || Tidebound::VaultVisit.q[:museum]
end
Tidebound::Actors.on_entry(:mother_at_vault, :seller_at_vault) do |_event, _actor|
  Tidebound::VaultVisit.q[:open] && !Tidebound::VaultVisit.q[:museum]
end
