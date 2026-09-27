# Loaded only by the disposable native fixture, before its Main driver.
module NativeScenarios
  module_function

  def run(scenario, output)
    species if %i[species all].include?(scenario)
    world(output) if %i[world all].include?(scenario)
  end

  def records_snapshot(klass, identifiers)
    identifiers.to_h do |identifier|
      record = klass.get(identifier.to_sym)
      attributes =
        record
          .instance_variables
          .reject { |name| name == :@pbs_file_suffix }
          .to_h do |name|
            value = record.instance_variable_get(name)
            # Essentials adds non-evolving family backlinks; retain all real rules.
            value = value.reject { |entry| entry[1] == :None }.sort_by(&:to_s) if name ==
              :@evolutions
            [name, value]
          end
      [identifier, attributes]
    end
  end

  def content_snapshot(inventory)
    {
      species: records_snapshot(GameData::Species, inventory.fetch("species")),
      metrics: records_snapshot(GameData::SpeciesMetrics, inventory.fetch("metrics"))
    }
  end

  def exact_asset!(expected, actual)
    unless actual && File.expand_path(actual) == File.expand_path(expected)
      raise "Asset resolved incorrectly: expected #{expected}, got #{actual.inspect}"
    end
  end

  def verify_art(inventory)
    inventory
      .fetch("art")
      .each do |asset|
        species, form = asset.fetch("species").to_sym, asset.fetch("form")
        [false, true].each do |shiny|
          [false, true].each do |back|
            key = (back ? "back" : "front") + (shiny ? "_shiny" : "")
            actual = GameData::Species.sprite_filename(species, form, 0, shiny, false, back)
            exact_asset!(asset.fetch(key), actual)
            image = AnimatedBitmap.new(actual)
            raise "Empty sprite: #{actual}" if image.bitmap.width == 0
            image.dispose
          end
          actual = GameData::Species.icon_filename(species, form, 0, shiny)
          exact_asset!(asset.fetch(shiny ? "icon_shiny" : "icon"), actual)
          image = AnimatedBitmap.new(actual)
          unless image.width >= image.height && image.width % image.height == 0
            raise "Icon must be a horizontal strip of square frames: #{actual}"
          end
          image.dispose
        end
        actual = GameData::Species.cry_filename(species, form)
        exact_asset!(asset.fetch("cry"), actual)
        raise "Missing cry: #{actual}" unless pbResolveAudioSE(actual)
      end
  end

  def species
    inventory = load_data("NativeContent.rxdata")
    expected = content_snapshot(inventory)
    sources = Dir.glob("NativePBS/pokemon*.txt").map { |path| File.expand_path(path) }
    raise "Species scenario requires PBS inputs" if sources.empty?
    # The shipped Linux tree is read-only. Compile into the isolated save area.
    destination = File.join(System.data_directory, "pbs-check")
    Dir.mkdir(destination)
    Dir.mkdir(File.join(destination, "Data"))
    Dir.chdir(destination) do
      Compiler.compile_pokemon(*sources.reject { |path| path =~ /pokemon_(forms|metrics)/ })
      Compiler.compile_pokemon_forms(*sources.select { |path| path.include?("pokemon_forms") })
      Compiler.compile_pokemon_metrics(*sources.select { |path| path.include?("pokemon_metrics") })
    end
    actual = content_snapshot(inventory)
    changed = []
    expected.each do |kind, records|
      records.each do |identifier, attributes|
        attributes.each do |name, value|
          found = actual.fetch(kind).fetch(identifier)[name]
          unless value == found
            changed << "#{identifier} #{name}: #{value.inspect} -> #{found.inspect}"
          end
        end
        extras = actual.fetch(kind).fetch(identifier).keys - attributes.keys
        changed << "#{identifier}: unexpected attributes #{extras}" unless extras.empty?
      end
    end
    raise "PBS compiler changed content: #{changed.join("; ")}" unless changed.empty?
    verify_art(inventory)
    puts "PASS: native PBS matches all custom species attributes and metrics; exact sprites, icons and cries resolve"
  end

  def capture(output, name)
    12.times do
      Graphics.update
      Input.update
      $scene.updateSpritesets
    end
    image = Graphics.snap_to_bitmap
    image.to_file(File.join(output, "world-#{name}.png"))
    image.dispose
  end

  def world(output)
    Game.start_new
    # Scene snapshots begin after the prelude; no retained or migrated saves.
    $scene = Scene_Map.new
    $scene.createSpritesets
    $PokemonSystem.textspeed = 3
    Tidebound.story[:opening_started] = true
    Tidebound.story[:bird_prelude_seen] = true
    Tidebound.story[:hall_talk] = true
    Tidebound.story[:walk_state] = :complete
    Tidebound.story[:household_pets] = Tidebound::Opening::HOUSE_PETS.to_h do |species, (name, _)|
      pokemon = Pokemon.new(species, 7, $player)
      pokemon.name = name
      Tidebound.state.assign_identity(pokemon)
      [species, pokemon]
    end
    pbChangePlayer(1)
    $player.party = [Pokemon.new(:NATU, 12, $player)]
    scenes = {
      home: [10, 8],
      coast: [34, 36],
      forest: [17, 25],
      lantern: [6, 6],
      vault: [12, 10],
      docks: [18, 18],
      road: [30, 55]
    }
    Graphics.transition(0)
    scenes.each do |name, (x, y)|
      Tidebound::World.travel(name, x, y)
      capture(output, name)
    end
    save_path = File.join(System.data_directory, "world-current.rxdata")
    raise "Fresh world save failed" unless Game.save(save_path)
    bytes = File.binread(save_path)
    $scene.dispose
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file(save_path))
    raise "Current world save changed during load" unless File.binread(save_path) == bytes
    raise "Current world save lost party" unless $player.party.first.species == :NATU
    puts "PASS: fresh current world scenes and real Game.save/Game.load roundtrip"
  ensure
    $scene.dispose if $scene.is_a?(Scene_Map) && $scene.map_renderer
  end
end
