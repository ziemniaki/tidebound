# Development-only Main. Never embedded in the release load manifest.
module DevelopmentScenario
  module_function

  def story_value(value)
    case value
    when Hash
      value.to_h { |key, item| [key.to_sym, story_value(item)] }
    when Array
      value.map { |item| story_value(item) }
    when String
      value.start_with?(":") ? value[1..].to_sym : value
    else
      value
    end
  end

  def seed
    spec = @spec
    return unless spec
    pbChangePlayer(spec.fetch("player").fetch("avatar"))
    $player.name = spec.fetch("player").fetch("name")
    $player.has_running_shoes = true
    $player.money = 0
    $PokemonSystem.textspeed = 3
    Tidebound.story.merge!(story_value(spec.fetch("story")))
    pokemon =
      spec
        .fetch("pokemon")
        .to_h do |key, record|
          species, form = record.fetch("species").split("_", 2)
          pet = Pokemon.new(species.to_sym, record.fetch("level"), $player)
          pet.form = form.to_i
          pet.reset_moves
          pet.name = record["name"] if record["name"]
          pet.item = record["item"].to_sym if record["item"]
          if record["moves"]
            pet.moves.clear
            record["moves"].each { |move| pet.learn_move(move.to_sym) }
          end
          Tidebound.state.assign_identity(pet)
          [key, pet]
        end
    $player.party = spec.fetch("party").map { |key| pokemon.fetch(key) }
    Tidebound.story[:household_pets] = spec
      .fetch("household")
      .to_h do |key|
        pet = pokemon.fetch(key)
        [pet.species, pet]
      end
    spec
      .fetch("bag")
      .each do |item, count|
        raise "Bag cannot hold #{count} #{item}" unless $bag.add(item.to_sym, count)
      end
    Tidebound.state.checkpoint = spec.fetch("checkpoint").dup
    $PokemonGlobal.pokecenterMapId = -1
  end

  # Game.start_new creates the map immediately after these values. Seed before
  # map-entry callbacks and autoruns can observe partially initialized quest state.
  module NewGameValues
    def load_new_game_values
      super
      DevelopmentScenario.seed
    end
  end

  def boot(spec)
    unless File.basename(System.data_directory).match?(
             /\ATidebound_(Scenario|Build_Smoke)_[a-f0-9]{32}\z/
           )
      raise "Scenarios require their own save namespace"
    end
    @spec = spec
    MessageTypes.load_default_messages if FileTest.exist?("Data/messages_core.dat")
    PluginManager.runPlugins
    Game.initialize
    SaveData.mark_values_as_unloaded
    SaveData.initialize_bootup_values
    pbSetResizeFactor([$PokemonSystem.screensize, 4].min)
    map, x, y, direction = spec.fetch("arrival")
    $data_system.start_map_id, $data_system.start_x, $data_system.start_y = map, x, y
    Game.start_new
    # The normal new-game wrapper installs the bird prelude. Scenarios enter the
    # declared map directly; its constructor hasn't allocated graphics resources.
    $scene = Scene_Map.new
    $game_player.direction = direction
    Tidebound::Actors.refresh($game_map)
    puts "Scenario #{spec.fetch("id")}: map #{map} at #{x},#{y}; saves #{System.data_directory}"
  ensure
    @spec = nil
  end

  def run(spec)
    boot(spec)
    $scene.main until $scene.nil?
  rescue StandardError => error
    message = "Scenario #{spec.fetch("id")}: #{error.full_message}"
    puts message
    File.write(File.join(System.data_directory, "scenario-error.txt"), message)
    raise
  end
end
SaveData.singleton_class.prepend(DevelopmentScenario::NewGameValues)
