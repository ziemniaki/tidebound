# The neighbour's keepsake and first dockside visit. Later sabre events stay reserved.
module Tidebound::VaultVisit
  GIFT = :TIDEBOUNDREEDCHARM
  module_function
  def q
    Tidebound.story[:vault_visit] ||= {}
  end
  def say(*lines)
    lines.each { |s| pbMessage(s) }
  end
  def hint
    return nil unless Tidebound::NeighborQuest.stage == :complete
    return "The oil seller has a small thank-you for you. Visit his shop." unless q[:gift]
    return "The seller has gone to the lighthouse. Speak to Mother in the hall." unless q[:open]
    unless q[:talk]
      return "Take the stairs down from the hall. Mother and the seller are at the vault."
    end
    unless q[:museum]
      return "Visit the museum at the docks. The city begins beside the old storehouse."
    end
    "You have seen the sabre in the dockside museum. Its history is still incomplete."
  end
  def reward
    return if q[:gift] || Tidebound::NeighborQuest.stage != :complete
    say(
      "Seller: Before you go. I brought this from home. Two blue reeds, just like the plate.",
      "Seller: Keep it. For bringing something precious back to an old fool."
    )
    return unless pbReceiveItem(GIFT)
    q[:gift] = true
    say(
      "Seller: I'll ask Ellie about that vault. I would rather carry this necklace up the hill once than lose it again."
    )
    e = Tidebound::World.actor(:oil_seller)
    if e
      e.through = true
      Tidebound::World.animate(e, [PBMoveRoute::DOWN] * 5 + [PBMoveRoute::RIGHT])
      e.opacity = 0
      e.through = true
    end
    # Show his departure on the existing coast, rather than teleporting him in dialogue.
    if $game_map.map_id == 106
      Tidebound::World.travel_coast(23, 13)
      e = Tidebound::World.actor(:seller_outside)
      e.moveto(*Tidebound::World.coast_xy(21, 12))
      e.opacity = 255
      e.through = true
      Tidebound::World.animate(e, [PBMoveRoute::DOWN] * 8 + [PBMoveRoute::LEFT] * 13)
      say("He stops to catch his breath, then takes the stone path towards the lighthouse.")
      Tidebound::World.animate(e, [PBMoveRoute::UP] * 5)
      e.opacity = 0
      e.through = true
    end
    sync
  end
  def mother
    say(
      "Mother: He tells me you found his necklace. Come here, love.",
      "She brushes a little road dust from your sleeve.",
      "Mother: We'll put it downstairs. There is a key for that door, too. This one stays with me."
    )
    m = Tidebound::World.actor(:mother)
    s = Tidebound::World.actor(:seller_at_home)
    [m, s].compact.each { |e| e.through = true }
    Tidebound::World.animate(m, [PBMoveRoute::LEFT] * 9 + [PBMoveRoute::DOWN] * 4) if m
    say(
      "Mother turns a small iron key. Cold air rises from the stairs.",
      "Mother: Mind the last step. It is lower than it looks."
    )
    q[:open] = true
    pbFadeOutIn { sync }
  end
  def stairs
    unless q[:open]
      say("The door is locked. A cool draught slips underneath it.")
      $game_player.moveto(4, 12)
      return
    end
    Tidebound::World.travel(:basement, 6, 13, 8)
  end
  def vault_door
    Tidebound::World.travel(:vault, 12, 15, 8)
  end
  def conversation
    Tidebound::World.erase_autorun
    return unless q[:open] && !q[:talk]
    Tidebound::World.animate($game_player, [PBMoveRoute::UP] * 5)
    say(
      "The seller places the wrapped necklace in a shallow drawer. Mother closes it with both hands.",
      "Seller: There. Safer than the drawer beside my socks.",
      "Mother: Most places are.",
      "Seller: You ought to see the museum down at the docks, child. They have a sabre there. Beautiful thing.",
      "Mother: Still on display?",
      "Seller: Last I heard. Beyond that old storehouse, along the quay. You cannot miss the museum sign.",
      "Mother: Go and have a look, then. There are things worth seeing beyond this shore.",
      "Seller: And give your legs a rest on the way. I should have taken my own advice."
    )
    q[:talk] = true
  end
  def city_gate
    unless q[:talk]
      say(
        (
          if q[:gift]
            "Before going farther, you should catch up with Mother and the seller at the lighthouse."
          else
            "The road reaches the docks here. First, there is an errand to finish for your neighbour."
          end
        )
      )
      $game_player.moveto(42, 43)
      $game_player.turn_left
      return
    end
    Tidebound::World.travel(:docks, 11, 28, 6)
  end
  def sabre
    if !q[:museum]
      say(
        "A long sabre rests behind glass. Its edge holds a thin, steady line of light.",
        "The label reads: SABRE. Maker unknown. The account of its arrival is incomplete.",
        "Someone has polished the fittings. The blade itself shows no sign of rust.",
        "You stay a moment longer than you intended."
      )
      q[:museum] = true
    else
      say("The sabre rests behind glass. There is still no maker named on the label.")
    end
  end
  def sync
    map = $game_map.map_id
    names =
      case map
      when 101
        { mother: !q[:open] || q[:museum], seller_at_home: q[:gift] && !q[:open] }
      when 106
        { oil_seller: !q[:gift] || q[:museum] }
      when 111
        { mother_at_vault: q[:open] && !q[:museum], seller_at_vault: q[:open] && !q[:museum] }
      else
        {}
      end
    names.each do |name, visible|
      e = Tidebound::World.actor(name)
      next unless e
      e.opacity = visible ? 255 : 0
      e.through = !visible
    end
  end
end
EventHandlers.add(
  :on_enter_map,
  :tidebound_vault_actors,
  proc { |_previous_map| Tidebound::VaultVisit.sync }
)
