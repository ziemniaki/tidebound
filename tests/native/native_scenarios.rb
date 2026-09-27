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

  # Verify custom definitions through real resolvers, not just filesystem presence.
  def verify_story_art
    GameData::Item.each do |item|
      next unless item.id.to_s.start_with?("TIDEBOUND")
      exact_asset!(
        "Graphics/Items/#{item.id}.png",
        pbResolveBitmap(GameData::Item.icon_filename(item.id))
      )
    end
    GameData::TrainerType.each do |trainer|
      next unless trainer.id.to_s.start_with?("TB")
      exact_asset!(
        "Graphics/Trainers/#{trainer.id}.png",
        pbResolveBitmap(GameData::TrainerType.front_sprite_filename(trainer.id))
      )
      sheet = Bitmap.new("Graphics/Characters/trainer_#{trainer.id}")
      unless sheet.width % 4 == 0 && sheet.height % 4 == 0
        raise "Invalid XP character sheet: #{trainer.id}"
      end
      sheet.dispose
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
    verify_story_art
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
    spec = load_data("NativeStart.rxdata")
    entered = false
    expected = DevelopmentScenario.story_value(spec.fetch("story"))
    EventHandlers.add(
      :on_enter_map,
      :native_start_state,
      proc do
        if expected
          unless expected.all? { |key, value| Tidebound.story[key] == value } &&
                   $bag.has?(:TIDEBOUNDPIE) && $player.party.first&.species == :NATU
            raise "Map entry observed incomplete state"
          end
          entered = true
        end
      end
    )
    DevelopmentScenario.boot(spec)
    expected = nil
    unless entered &&
             [$game_map.map_id, $game_player.x, $game_player.y, $game_player.direction] ==
               spec.fetch("arrival")
      raise "Playtest did not start at the declared state/entrance"
    end
    $scene.createSpritesets
    interrupt_route
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
    identity = $player.party.map { |pet| [Tidebound.identity(pet), pet.item_id] }
    story = Marshal.dump(Tidebound.story)
    save_path = File.join(System.data_directory, "world-current.rxdata")
    raise "Fresh world save failed" unless Game.save(save_path)
    bytes = File.binread(save_path)
    $scene.dispose
    SaveData.mark_values_as_unloaded
    saved = SaveData.get_data_from_file(save_path)
    # Simulate a save from before repacking. Boot normally loads game_system first.
    $game_system = saved[:game_system]
    $game_system.magic_number = $data_system.magic_number ^ 1
    tile = $game_map.data[0, 0, 0]
    saved[:map_factory].map.data[0, 0, 0] = tile + 1
    Game.load(saved)
    raise "Save retained stale map tiles" unless $game_map.data[0, 0, 0] == tile
    unless identity == $player.party.map { |pet| [Tidebound.identity(pet), pet.item_id] } &&
             Marshal.dump(Tidebound.story) == story
      raise "Save lost companion identity, held items or quest state"
    end
    raise "Current world save changed during load" unless File.binread(save_path) == bytes
    raise "Current world save lost party" unless $player.party.first.species == :NATU
    puts "PASS: declared start before map callbacks; world captures; native save/load preserves state and refreshes stale maps"
  ensure
    $scene.dispose if $scene.is_a?(Scene_Map) && $scene.map_renderer
  end

  def interrupt_route
    actor = Tidebound::World.actor(:mother)
    original = [actor.x, actor.y, actor.through, actor.opacity, actor.move_speed]
    route = actor.instance_variable_get(:@move_route)
    begin
      Tidebound::Scenes.run(actor, restore_positions: true) do
        actor.opacity = 80
        actor.move_speed = 2
        pbMoveRoute(actor, [PBMoveRoute::WAIT, 200, PBMoveRoute::DOWN])
        raise "Interrupted native scene"
      end
    rescue RuntimeError => error
      raise unless error.message == "Interrupted native scene"
    end
    unless !actor.move_route_forcing && actor.instance_variable_get(:@move_route).equal?(route) &&
             !Tidebound::Scenes.owns?(actor) &&
             original == [actor.x, actor.y, actor.through, actor.opacity, actor.move_speed]
      raise "Interrupted scene retained temporary movement/presentation"
    end
    10.times { actor.update }
    raise "Cancelled route resumed" unless [actor.x, actor.y] == original.first(2)
    puts "PASS: native forced-route interruption restores actor state and cancels pending movement"
  end
end
