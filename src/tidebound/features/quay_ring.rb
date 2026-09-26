# Repeatable encounters use real Essentials teams and the normal death rules.
module Tidebound::QuayRing
  module_function
  COOLDOWN = 15 * 60
  # Entire exceptional families are barred, including the regional pseudo branch.
  EXCLUDED_ROOTS = %i[
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
    WURMPLE
  ].freeze
  REGIONAL = %i[PSYDUCK EKANS ARBOK SUNKERN].freeze
  NAMES = %w[Bram Corin Della Ewan Fen Hali Jory Kest Lorn Mina Orla Pell Renn Sable Tavi].freeze
  def state
    Tidebound.story[:quay_ring] ||= {}
  end
  def remaining(now = Time.now.to_i)
    return 0 unless state[:last_battle]
    [[COOLDOWN - (now - state[:last_battle]), 0].max, COOLDOWN].min
  end
  def eligible?(data, level)
    return false unless data.form == 0 || (data.form == 1 && REGIONAL.include?(data.species))
    return false if data.form == 0 && REGIONAL.include?(data.species)
    return false if %w[Legendary Mythical UltraBeast].any? { |flag| data.has_flag?(flag) }
    return false if EXCLUDED_ROOTS.include?(data.get_baby_species)
    return false if %i[FROSTCOON NIVALORA].include?(data.species)
    return false if data.minimum_level > level
    # Stone/trade evolutions have low minimum_level: a stat ceiling checks these too.
    ceiling = level < 12 ? 350 : level < 20 ? 430 : level < 30 ? 490 : 580
    return false if data.base_stats.values.sum > ceiling
    learned = data.moves.select { |at, _move| at <= level }.map(&:last).uniq.last(4)
    return false unless learned.any? { |move| GameData::Move.get(move).power > 0 }
    true
  end
  def catalog
    @catalog ||=
      begin
        entries = []
        GameData::Species.each do |data|
          next if data.form != 0 && !(data.form == 1 && REGIONAL.include?(data.species))
          # Only species with shipped battle artwork can enter the ring.
          next unless pbResolveBitmap("Graphics/Pokemon/Front/#{data.id}")
          entries << data
        end
        entries
      end
  end
  def roster(party, dex, rng = Random.new, entries = catalog)
    levels = party.reject(&:egg?).select { |pkmn| pkmn.hp > 0 }.map(&:level).sort.reverse.first(3)
    used = []
    levels.map do |anchor|
      level = [1, anchor - rng.rand(1..3)].max
      pool = entries.select { |data| eligible?(data, level) }
      unique = pool.reject { |data| used.include?(data.species) }
      pool = unique unless unique.empty?
      seen, unseen = pool.partition { |data| dex.seen?(data.species) }
      preferred = rng.rand(100) < 80 ? seen : unseen
      preferred = pool if preferred.empty?
      raise "No suitable quay challenger for level #{level}" if preferred.empty?
      data = preferred[rng.rand(preferred.length)]
      used << data.species
      [data.species, data.form, level]
    end
  end
  def offer
    state[:offer] ||= { name: NAMES.sample, team: roster($player.party, $player.pokedex) }
  end
  def challenger(ticket)
    foe =
      Tidebound::Encounters.trainer(:SAILOR, ticket[:name], "Enough. You've earned the purse.", [])
    ticket[:team].each do |species, form, level|
      pokemon = Pokemon.new(species, level)
      pokemon.form = form
      pokemon.reset_moves
      pokemon.calc_stats
      foe.party << pokemon
    end
    foe
  end
  def talk
    if remaining > 0
      pbMessage(
        _INTL(
          "Bookkeeper: Next challenger in {1} minutes. Let them get their breath back.",
          (remaining / 60.0).ceil
        )
      )
      return
    end
    return unless Tidebound::Encounters.able?
    ticket = offer
    levels = ticket[:team].map { |row| row[2] }
    pbMessage(
      _INTL(
        "Bookkeeper: {1} is taking challenges. {2} companions, levels {3}. No entry fee. The crowd pays the purse.",
        ticket[:name],
        levels.length,
        levels.join(", ")
      )
    )
    unless pbConfirmMessage("Fight in the quay ring? Defeat carries the usual risk of death.")
      return
    end
    # Recheck changed parties without rerolling a declined offer. Never force extra foes.
    anchors =
      $player.party.reject(&:egg?).select { |p| p.hp > 0 }.map(&:level).sort.reverse.first(3)
    if ticket[:team].length > anchors.length ||
         ticket[:team].each_with_index.any? { |row, i| row[2] > [1, anchors[i].to_i - 1].max }
      pbMessage("Bookkeeper: Your team's changed. I'll find someone better matched. Ask me again.")
      state.delete(:offer)
      return
    end
    result = Tidebound.trainer!(challenger(ticket))
    return if result == 0 || result.nil?
    state[:last_battle] = Time.now.to_i
    state.delete(:offer)
    if result == :astral
      Tidebound::World.travel(:astral, 15, 21, 8)
    elsif result == 1
      state[:wins] = state.fetch(:wins, 0) + 1
      purse = 60 + levels.sum * 5
      $player.money += purse
      pbMessage(
        _INTL(
          "The bookkeeper counts out {1} coins. Beyond the ropes, somebody tears up a betting slip.",
          purse
        )
      )
    end
  end
end
