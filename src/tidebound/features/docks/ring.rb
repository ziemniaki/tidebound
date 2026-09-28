# Dockside bouts: one saved offer per quarter-hour, using ordinary battle recovery.
module Tidebound::DockRing
  INTERVAL = 900
  NAMES = %w[Hale Brin Cass Fen Ludo Orla Venn].freeze
  # Working animals, shore scavengers and brawlers. Fish, legendary spectacles
  # and unsuitable forms do not become ring opponents merely by being seen.
  ROSTER = %i[
    RATTATA
    RATICATE
    MEOWTH
    PERSIAN
    MANKEY
    PRIMEAPE
    MACHOP
    MACHOKE
    SANDSHREW
    SANDSLASH
    GEODUDE
    GRAVELER
    NATU
    AIPOM
    SNUBBULL
    GRANBULL
    TYROGUE
    HITMONLEE
    HITMONCHAN
    HITMONTOP
    MAKUHITA
    HARIYAMA
    MEDITITE
    MEDICHAM
    POOCHYENA
    MIGHTYENA
    ZIGZAGOON
    LINOONE
    CORPHISH
    CRAWDAUNT
    CROAGUNK
    TOXICROAK
    SCRAGGY
    SCRAFTY
    PANCHAM
    PANGORO
  ].freeze
  PSEUDO_FAMILIES = %i[
    DRATINI
    LARVITAR
    BAGON
    BELDUM
    GIBLE
    DEINO
    GOOMY
    JANGMOO
    DREEPY
    FRIGIBAX
  ].freeze
  module_function

  def flags
    Tidebound.story[:dock_ring] ||= {}
  end

  def eligible?(data, level)
    return false unless data.form == 0 && ROSTER.include?(data.id)
    return false if %w[Legendary Mythical UltraBeast].any? { |flag| data.has_flag?(flag) }
    return false if data.base_stat_total >= 600 || PSEUDO_FAMILIES.include?(data.get_baby_species)
    return false if data.minimum_level > level
    moves =
      data.moves.select { |learned, _move| learned <= level }.map(&:last).reverse.uniq.first(4)
    moves.any? { |move| GameData::Move.get(move).power > 0 }
  end

  def party_levels
    $player.party.select { |pet| !pet.egg? && pet.hp > 0 }.map(&:level).sort
  end

  def generate_team(levels, rng)
    middle = levels.length / 2
    typical = (levels[(levels.length - 1) / 2] + levels[middle]) / 2
    chosen = []
    Array.new([levels.length, 3].min) do
      level = [typical - (1 + rng.rand(3)), 1].max
      candidates =
        ROSTER.filter_map do |id|
          data = GameData::Species.try_get(id)
          id if data && eligible?(data, level) && !chosen.include?(id)
        end
      familiar, unfamiliar = candidates.partition { |id| $player.pokedex.seen?(id) }
      pool = rng.rand(100) < 80 ? familiar : unfamiliar
      pool = candidates if pool.empty?
      # The roster has several legal level-one attackers, even for a new party.
      species = pool.fetch(rng.rand(pool.length))
      chosen << species
      [species, level]
    end
  end

  def offer(now = Time.now.to_i)
    levels = party_levels
    return nil if levels.empty?
    current = flags[:offer]
    if !current || now >= current[:expires_at]
      current =
        flags[:offer] = {
          seed: rand(0x7fffffff),
          name: NAMES.sample,
          expires_at: now + INTERVAL,
          used: false
        }
    end
    # Rebalance for a changed active party without resetting the saved clock.
    if current[:levels] != levels
      current[:team] = generate_team(levels, Random.new(current[:seed]))
      current[:levels] = levels
    end
    current
  end

  def challenge
    return unless Tidebound::Encounters.able?
    current = offer
    if current[:used]
      minutes = [(current[:expires_at] - Time.now.to_i + 59) / 60, 1].max
      pbMessage("Harker: That berth is finished. Another challenger in about #{minutes} minute(s).")
      return
    end
    roster =
      current[:team].map { |id, level| "#{GameData::Species.get(id).name} Lv. #{level}" }.join(", ")
    pbMessage("Harker: #{current[:name]} is waiting. #{roster}.")
    unless pbConfirmMessage(
             "Enter the dock ring? Your companions face the same danger as in any battle."
           )
      return
    end
    result =
      Tidebound::Encounters.trainer(
        type: :SAILOR,
        name: current[:name],
        loss: "Enough. Call it.",
        team: current[:team],
        departure: "The coins keep changing hands after the harbour falls away."
      )
    # Aborted battles leave the exact offer available; defeat must never count as a win.
    current[:used] = true if [1, 2, 3, 5, :astral].include?(result)
    return unless result == 1
    flags[:wins] = flags.fetch(:wins, 0) + 1
    pbMessage("Harker marks the slate. Behind him, someone quietly counts out a week's pay.")
  end

  def watch
    pbMessage(
      "Machop drives forward. Hitmonlee answers with a kick. The ropes jerk; the sailors lean closer."
    )
    pbMessage("A voice calls a price. Nobody asks the two in the ring.")
  end

  def board
    pbMessage(
      "THE QUARTER-HOUR RING. Speak to Harker below the ropes. One bout per challenger. No house healing."
    )
    pbMessage("A greasy slate lists the bets. Beside it, a bucket of water has turned pink.")
  end
end
