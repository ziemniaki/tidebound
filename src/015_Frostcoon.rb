# Refresh cached values in previously owned provisional Frostcoon, once.
# Revision 2 adds the support moveset; keep HP, status, items and identity.
module Tidebound
  module Frostcoon
    module_function
    # Preserve selected support moves; replace attacks without refilling their PP.
    def support_moves(pokemon)
      learned = pokemon.getMoveList.select { |lv, _| lv <= pokemon.level }.map(&:last)
      priority = [:SPIKES, :WISH, :STUNSPORE, :PROTECT, :RAINDANCE, :LIFEDEW,
                  :STICKYWEB, :SLEEPPOWDER, :HAIL, :AURORAVEIL]
      candidates = (priority + learned.reverse).uniq.select { |m| learned.include?(m) }
      retained = pokemon.moves.select { |m| GameData::Move.get(m.id).category == 2 }
      used = retained.map(&:id)
      pokemon.moves.map! do |move|
        next move if GameData::Move.get(move.id).category == 2
        replacement = candidates.find { |m| !used.include?(m) }
        next nil unless replacement
        used << replacement
        fresh = Pokemon::Move.new(replacement)
        fresh.pp = [move.pp, fresh.total_pp].min
        fresh
      end
      pokemon.moves.compact!
      pokemon.learn_move(:STRINGSHOT) if pokemon.moves.empty?
    end

    def refresh(pokemon)
      return unless pokemon && pokemon.species == :FROSTCOON
      revision = pokemon.instance_variable_get(:@tidebound_frostcoon_revision).to_i
      return if revision >= 2
      if revision < 1
        hp = pokemon.hp
        pokemon.ability = nil if pokemon.ability_id == :SHEDSKIN
        pokemon.calc_stats
        pokemon.hp = [hp, pokemon.totalhp].min
      end
      support_moves(pokemon)
      pokemon.instance_variable_set(:@tidebound_frostcoon_revision, 2)
    end

    def refresh_loaded
      $player.party.each { |p| refresh(p) } if $player
      if $PokemonStorage
        $PokemonStorage.maxBoxes.times do |box|
          $PokemonStorage.maxPokemon(box).times { |slot| refresh($PokemonStorage[box, slot]) }
        end
      end
      if $tidebound
        ($tidebound.souls + $tidebound.memorials).each { |s| refresh(s.pokemon) }
      end
    end
  end

  module FrostcoonSaveRefresh
    def load_all_values(*args)
      result = super
      Tidebound::Frostcoon.refresh_loaded
      result
    end
  end
end
SaveData.singleton_class.prepend(Tidebound::FrostcoonSaveRefresh)

module Tidebound
  module FrostcoonEvolutionMoves
    def species=(value)
      previous_species = species
      result = super
      if previous_species != :FROSTCOON && species == :FROSTCOON
        Tidebound::Frostcoon.support_moves(self)
        instance_variable_set(:@tidebound_frostcoon_revision, 2)
      end
      result
    end
  end
end
Pokemon.prepend(Tidebound::FrostcoonEvolutionMoves)
