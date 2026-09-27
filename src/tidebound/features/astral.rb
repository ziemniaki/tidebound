# Recurring journeys, spirit recovery and memorial interactions.
module Tidebound::Astral
  module_function

  def arrival
    Tidebound::World.erase_autorun
    return unless Tidebound.state.realm == :astral
    # The arrival message runs once per journey, including after save/reload.
    unless Tidebound.story[:astral_arrival_journey] == Tidebound.state.journey
      Tidebound.story[:astral_arrival_journey] = Tidebound.state.journey
      pbMessage("No wind. No footsteps.\nNo familiar weight beside you.")
      pbMessage("Somewhere in the fog, a familiar cry answers itself.")
    end
    give_guide
  end

  def give_guide
    Tidebound.borrow_guide! if $player.able_pokemon_count == 0
    unless Tidebound.story[:astral_balls_journey] == Tidebound.state.journey
      Tidebound.story[:astral_balls_journey] = Tidebound.state.journey
      $bag.add(:POKEBALL, 18)
    end
  end

  def guide
    give_guide
    pbMessage("Traveller: You can hear them. That is something.")
    pbMessage("Traveller: This bird will keep you company here. It cannot cross with you.")
    pbMessage(
      "Find your companions in the fog. Each allows one encounter: catch them before six turns pass. If they faint, you flee, or time runs out, they are lost."
    )
    pbMessage("Traveller: The way back is behind me. Leave no one you still mean to find.")
  end

  def spirit(index)
    record = Tidebound.state.souls[index]
    return unless record && record.status == :waiting
    give_guide
    pbMessage("#{record.pokemon.name} turns at the sound of your voice.")
    unless pbConfirmMessage(
             "Reach for #{record.pokemon.name}? There is one encounter, with six turns to catch them. Failure is permanent."
           )
      return
    end
    result = Tidebound.recover_spirit!(record.id)
    if result == :recovered
      pbMessage(
        "A familiar weight settles against you.\n#{record.pokemon.name} has returned, weak but real."
      )
    else
      pbMessage("For an instant, #{record.pokemon.name} seems to recognize you.")
      pbMessage("Then the shape is gone.")
    end
  end

  def leave
    return unless Tidebound.state.realm == :astral
    remaining = Tidebound.state.waiting_ids.length
    prompt =
      if remaining > 0
        "#{remaining} #{remaining == 1 ? "companion still waits" : "companions still wait"} in the fog. Leaving will lose them permanently. Return to the living shore?"
      else
        "The shore is very far away. Return to it?"
      end
    unless pbConfirmMessageSerious(prompt)
      $game_player.moveto(15, 21)
      $game_player.turn_up
      return
    end
    no_survivors = $player.party.none? { |p| !Tidebound.borrowed?(p) }
    point = Tidebound.return_to_living!
    Tidebound::World.travel(*point)
    if no_survivors
      pbMessage("A small Natu waits beside you. It is not the bird you lost.")
    else
      pbMessage("Cold air. The weight of your own body.\nSomeone has kept a place for you.")
    end
  end

  def memorial
    lost = Tidebound.state.memorials
    if lost.empty?
      pbMessage("There are small hollows in the stone.\nNone yet carries a name.")
    else
      labels = lost.map { |s| "#{s.pokemon.name} - #{s.pokemon.speciesName}" }
      choice = pbMessage("The stone remembers.", labels + ["Step away"], -1)
      if choice >= 0 && choice < lost.length
        pkmn = lost[choice].pokemon
        pbMessage(
          "#{pkmn.name}.\nLevel #{pkmn.level}.\nThere was a time when this name brought them running."
        )
      end
    end
  end
end

Tidebound::Actors.on_frame("spirit") do |_event, actor|
  soul = Tidebound.state.souls[actor.fetch("index")]
  soul && soul.status == :waiting && Tidebound.state.realm == :astral
end
