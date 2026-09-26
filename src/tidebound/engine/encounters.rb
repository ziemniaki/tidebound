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
    result = Tidebound.wild!(*foes)
    if result == :astral
      pbMessage("The sound of the world draws away.")
      Tidebound::World.travel(:astral, 15, 21, 8)
    end
    result
  end
  def trainer(type, name, loss, team)
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
    foe
  end
end
