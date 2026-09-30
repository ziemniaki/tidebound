# Encounter setup shared by visible wilds and trainer quests.
module Tidebound::Encounters
  module_function
  def able?
    return true if Tidebound.state.realm == :living && $player.able_pokemon_count > 0
    pbMessage(
      "Your companions need a little strength before facing anyone. A travelling ninja's fire can help."
    )
    false
  end
  def fight(*foes)
    finish(Tidebound.wild!(*foes), "The sound of the world draws away.")
  end
  def trainer(type:, name:, loss:, team:, departure: "The sound of the world draws away.")
    foe = NPCTrainer.new(name, type)
    foe.lose_text = loss
    team.each do |species, level, moves|
      pokemon = Pokemon.new(species, level, foe)
      if moves
        pokemon.moves.clear
        moves.each { |move| pokemon.learn_move(move) }
      end
      foe.party << pokemon
    end
    finish(Tidebound.trainer!(foe), departure)
  end

  def finish(result, departure)
    if result == :astral
      pbMessage(departure) if departure
      Tidebound::World.travel(:astral, 15, 21, 8)
    end
    result
  end
  private_class_method :finish
end

# Native random encounters, including caves, use the same pre-cleanup loss
# snapshot as visible wilds throughout the authored living world.
module Tidebound::LivingWildBattles
  def start(*args, can_override: false)
    if can_override && Tidebound::World::MAP_IDS.include?($game_map.map_id) &&
         Tidebound.state.realm == :living
      result = Tidebound::Encounters.fight(*args)
      return ![2, 5, :astral].include?(result)
    end
    super
  end
end
WildBattle.singleton_class.prepend(Tidebound::LivingWildBattles)
