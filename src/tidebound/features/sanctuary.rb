# A period-appropriate front end to the existing, normally serialized storage.
# Transfers keep the actual individual, including injuries, moves and held items.
module Tidebound::Sanctuary
  PAGE_SIZE = 10
  module_function

  def stored
    result = []
    $PokemonStorage.maxBoxes.times do |box|
      $PokemonStorage
        .maxPokemon(box)
        .times do |slot|
          pet = $PokemonStorage[box, slot]
          result << [box, slot, pet] if pet
        end
    end
    result
  end

  def able?(pet)
    pet && !pet.egg? && pet.hp > 0 && !Tidebound.borrowed?(pet)
  end

  def may_remove?(index)
    pet = $player.party[index]
    pet && !Tidebound.borrowed?(pet) &&
      $player.party.each_with_index.any? { |other, i| i != index && able?(other) }
  end

  def deposit(index)
    return false unless Tidebound.state.realm == :living && may_remove?(index)
    $PokemonStorage.maxBoxes.times do |box|
      slot = $PokemonStorage.pbFirstFreePos(box)
      next if slot < 0
      $PokemonStorage[box, slot] = $player.party[index]
      $player.party.delete_at(index)
      return true
    end
    false
  end

  def withdraw(box, slot)
    return false unless Tidebound.state.realm == :living && $player.party.length < 6
    unless box.between?(0, $PokemonStorage.maxBoxes - 1) &&
             slot.between?(0, $PokemonStorage.maxPokemon(box) - 1)
      return false
    end
    pet = $PokemonStorage[box, slot]
    return false unless pet && !Tidebound.borrowed?(pet)
    $player.party << pet
    $PokemonStorage[box, slot] = nil
    true
  end

  def exchange(index, box, slot)
    return false unless Tidebound.state.realm == :living
    unless box.between?(0, $PokemonStorage.maxBoxes - 1) &&
             slot.between?(0, $PokemonStorage.maxPokemon(box) - 1)
      return false
    end
    outgoing, incoming = $player.party[index], $PokemonStorage[box, slot]
    unless outgoing && incoming && !Tidebound.borrowed?(outgoing) && !Tidebound.borrowed?(incoming)
      return false
    end
    return false unless able?(incoming) || may_remove?(index)
    $player.party[index], $PokemonStorage[box, slot] = incoming, outgoing
    true
  end

  def label(pet)
    "#{pet.name} / #{pet.speciesName} Lv.#{pet.level} (HP #{pet.hp}/#{pet.totalhp})"
  end

  def choose_party
    choice = pbMessage("Who should stay here?", $player.party.map { |p| label(p) } + ["Leave"], -1)
    choice if choice >= 0 && choice < $player.party.length
  end

  def choose_stored
    entries = stored
    if entries.empty?
      pbMessage("No companions are resting here yet.")
      return nil
    end
    page = 0
    loop do
      group = entries.slice(page * PAGE_SIZE, PAGE_SIZE)
      options = group.map { |record| label(record[2]) }
      actions = group.map { |record| record }
      if (page + 1) * PAGE_SIZE < entries.length
        options << "Next page"
        actions << :next
      end
      if page > 0
        options << "Previous page"
        actions << :previous
      end
      options << "Leave"
      choice = pbMessage("Resting companions: #{entries.length}", options, -1)
      return nil if choice < 0 || choice >= actions.length
      selected = actions[choice]
      return selected if selected.is_a?(Array)
      page += selected == :next ? 1 : -1
    end
  end

  def open
    return unless Tidebound.state.realm == :living
    pbMessage(
      "The refuge keeps a place for every companion. Those beyond your travelling six wait here safely."
    )
    loop do
      choice =
        pbMessage(
          "Who will travel with you?",
          ["Invite a resting companion", "Let a companion rest", "Exchange companions", "Leave"],
          -1
        )
      break if choice < 0 || choice >= 3
      case choice
      when 0
        if $player.party.length >= 6
          pbMessage(
            "Six companions already travel with you. Exchange one, or let someone rest first."
          )
          next
        end
        selected = choose_stored
        withdraw(*selected.first(2)) if selected
      when 1
        index = choose_party
        if index && !deposit(index)
          pbMessage(
            "Keep at least one able companion with you. The refuge also needs a free place."
          )
        end
      when 2
        selected = choose_stored
        next unless selected
        index = choose_party
        if index && !exchange(index, *selected.first(2))
          pbMessage("You need an able companion to travel with you.")
        end
      end
    end
  end
end
