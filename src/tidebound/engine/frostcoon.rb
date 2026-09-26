# Apply the current support moveset when a Wurmple evolves into Frostcoon.
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

  end

  module FrostcoonEvolutionMoves
    def species=(value)
      previous_species = species
      result = super
      if previous_species != :FROSTCOON && species == :FROSTCOON
        Tidebound::Frostcoon.support_moves(self)
      end
      result
    end
  end
end
Pokemon.prepend(Tidebound::FrostcoonEvolutionMoves)
