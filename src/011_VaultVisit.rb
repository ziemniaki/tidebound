# The neighbour's keepsake and first dockside visit. Later sabre events stay reserved.
module Tidebound::VaultVisit
  GIFT=:TIDEBOUNDREEDCHARM
  module_function
  def q; Tidebound::Opening.flags[:vault_visit] ||= {}; end
  def say(*lines); lines.each { |s| pbMessage(s) }; end
  def actor(name); Tidebound::Opening.actor(name); end
  def hint
    return nil unless Tidebound::NeighborQuest.stage==:complete
    return 'The oil seller has a small thank-you for you. Visit his shop.' unless q[:gift]
    return 'The seller has gone to the lighthouse. Speak to Mother in the hall.' unless q[:open]
    return 'Take the stairs down from the hall. Mother and the seller are at the vault.' unless q[:talk]
    return 'Visit the museum at the docks. The city begins beside the old storehouse.' unless q[:museum]
    'You have seen the sabre in the dockside museum. Its history is still incomplete.'
  end
  def reward
    return if q[:gift] || Tidebound::NeighborQuest.stage!=:complete
    say('Seller: Before you go. I brought this from home. Two blue reeds, just like the plate.',
        'Seller: Keep it. For bringing something precious back to an old fool.')
    return unless pbReceiveItem(GIFT)
    q[:gift]=true
    say("Seller: I'll ask Ellie about that vault. I would rather carry this necklace up the hill once than lose it again.")
    e=actor('Oil seller')
    if e
      e.through=true
      Tidebound::Opening.animate(e,[PBMoveRoute::DOWN]*5+[PBMoveRoute::RIGHT])
      e.opacity=0; e.through=true
    end
    # Show his departure on the existing coast, rather than teleporting him in dialogue.
    if $game_map.map_id==106
      Tidebound::Opening.travel_coast(23,13)
      e=actor('Seller outside'); e.moveto(*Tidebound::Opening.coast_xy(21,12));e.opacity=255;e.through=true
      Tidebound::Opening.animate(e,[PBMoveRoute::DOWN]*8+[PBMoveRoute::LEFT]*13)
      say('He stops to catch his breath, then takes the stone path towards the lighthouse.')
      Tidebound::Opening.animate(e,[PBMoveRoute::UP]*5)
      e.opacity=0; e.through=true
    end
    sync
  end
  def mother
    say('Mother: He tells me you found his necklace. Come here, love.',
        'She brushes a little road dust from your sleeve.',
        "Mother: We'll put it downstairs. There is a key for that door, too. This one stays with me.")
    m=actor('Mother');s=actor('Seller at home')
    [m,s].compact.each { |e| e.through=true }
    Tidebound::Opening.animate(m,[PBMoveRoute::LEFT]*9+[PBMoveRoute::DOWN]*4) if m
    say('Mother turns a small iron key. Cold air rises from the stairs.',
        'Mother: Mind the last step. It is lower than it looks.')
    q[:open]=true
    pbFadeOutIn { sync }
  end
  def stairs
    unless q[:open]
      say('The door is locked. A cool draught slips underneath it.')
      $game_player.moveto(4,12)
      return
    end
    Tidebound::Opening.travel(110,6,13,8)
  end
  def vault_door
    Tidebound::Opening.travel(111,12,15,8)
  end
  def conversation
    Tidebound::Opening.erase_autorun
    return unless q[:open] && !q[:talk]
    Tidebound::Opening.animate($game_player,[PBMoveRoute::UP]*5)
    say('The seller places the wrapped necklace in a shallow drawer. Mother closes it with both hands.',
        'Seller: There. Safer than the drawer beside my socks.',
        'Mother: Most places are.',
        'Seller: You ought to see the museum down at the docks, child. They have a sabre there. Beautiful thing.',
        'Mother: Still on display?',
        'Seller: Last I heard. Beyond that old storehouse, along the quay. You cannot miss the museum sign.',
        'Mother: Go and have a look, then. There are things worth seeing beyond this shore.',
        'Seller: And give your legs a rest on the way. I should have taken my own advice.')
    q[:talk]=true
  end
  def city_gate
    unless q[:talk]
      say(q[:gift] ? 'Before going farther, you should catch up with Mother and the seller at the lighthouse.' : 'The road reaches the docks here. First, there is an errand to finish for your neighbour.')
      $game_player.moveto(42,43);$game_player.turn_left
      return
    end
    Tidebound::Opening.travel(112,11,28,6)
  end
  def sabre
    if !q[:museum]
      say('A long sabre rests behind glass. Its edge holds a thin, steady line of light.',
          'The label reads: SABRE. Maker unknown. The account of its arrival is incomplete.',
          'Someone has polished the fittings. The blade itself shows no sign of rust.',
          'You stay a moment longer than you intended.')
      q[:museum]=true
    else
      say('The sabre rests behind glass. There is still no maker named on the label.')
    end
  end
  def sync
    map=$game_map.map_id
    names = case map
    when 101 then {'Mother'=>!q[:open] || q[:museum], 'Seller at home'=>q[:gift] && !q[:open]}
    when 106 then {'Oil seller'=>!q[:gift] || q[:museum]}
    when 111 then {'Mother at vault'=>q[:open] && !q[:museum], 'Seller at vault'=>q[:open] && !q[:museum]}
    else {}; end
    names.each do |name,visible|
      e=actor(name);next unless e
      e.opacity=visible ? 255 : 0;e.through=!visible
    end
  end
end
module Tidebound::VaultOpeningHooks
  def oil_seller
    if Tidebound::NeighborQuest.stage==:complete && !Tidebound::VaultVisit.q[:gift]
      Tidebound::VaultVisit.reward
    else
      super
      Tidebound::VaultVisit.reward if Tidebound::NeighborQuest.stage==:complete && !Tidebound::VaultVisit.q[:gift]
    end
  end
  def mother
    v=Tidebound::VaultVisit
    if v.q[:gift] && !v.q[:open];v.mother
    elsif v.q[:museum];pbMessage('Mother: Did you find the museum? Good. I am glad you went.');
    else;super;end
  end
end
Tidebound::Opening.singleton_class.prepend(Tidebound::VaultOpeningHooks)
module Tidebound::VaultHints
  def hint; Tidebound::VaultVisit.hint || super; end
end
Tidebound::NeighborQuest.singleton_class.prepend(Tidebound::VaultHints)
EventHandlers.add(:on_new_spriteset_map,:tidebound_vault_actors,proc { |_s,_v| Tidebound::VaultVisit.sync })
