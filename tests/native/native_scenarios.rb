# Loaded only by the disposable native fixture, before its Main driver.
module NativeScenarios
  module_function

  def run(scenario, output)
    window_scaling if %i[runtime all].include?(scenario)
    species if %i[species all].include?(scenario)
    world(output) if %i[world all].include?(scenario)
  end

  def window_scaling
    original_size = $PokemonSystem.screensize
    unless Graphics.fixed_aspect_ratio && Graphics.integer_scaling && Graphics.last_mile_scaling
      raise "Game does not fit the window with proportional scaling"
    end
    unless [true, 1].include?(Graphics.smooth_scaling)
      raise "Fractional window scaling is not bilinear"
    end
    pbSetResizeFactor(1)
    [[320, 240], [640, 480], [720, 400], [400, 600]].each do |width, height|
      Graphics.resize_window(width, height)
      20.times do
        Graphics.update
        Input.update
      end
      unless (Graphics.scale - height.to_f / Settings::SCREEN_HEIGHT).abs < 0.01
        raise "Native window did not resize to #{width}x#{height}"
      end
      image = Graphics.snap_to_bitmap
      begin
        unless image.width == Settings::SCREEN_WIDTH && image.height == Settings::SCREEN_HEIGHT
          raise "Window resizing changed the logical game canvas"
        end
      ensure
        image.dispose
      end
    end
    puts "PASS: native window resizing preserves the game canvas at small, large, wide and tall sizes"
  ensure
    pbSetResizeFactor(original_size)
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

  def map_passages
    surfing = $PokemonGlobal.surfing
    $PokemonGlobal.surfing = false
    Tidebound::MAP_PASSAGES.each do |id, rows|
      map = Game_Map.new
      map.setup(id)
      rows.each_with_index do |row, y|
        row.each_char.with_index do |value, x|
          passage = [2, 4, 6, 8].all? { |direction| map.playerPassable?(x, y, direction) }
          raise "Native tile collision differs at #{id}/#{x},#{y}" unless passage == (value == "1")
        end
      end
      next unless id == 108
      $PokemonGlobal.surfing = true
      map.height.times do |y|
        map.width.times do |x|
          next unless map.terrain_tag(x, y).id == :StillWater
          raise "Pond tile cannot be surfed: #{x},#{y}" unless map.playerPassable?(x, y, 2)
        end
      end
      $PokemonGlobal.surfing = false
    end
    puts "PASS: native passage flags match all #{Tidebound::MAP_PASSAGES.length} authored maps; pond water supports Surf"
  ensure
    $PokemonGlobal.surfing = surfing
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
    map_passages
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
    relocating_npc_floor
    furniture_overhangs(output)
    scenes.each do |name, (x, y)|
      Tidebound::World.travel(name, x, y)
      capture(output, name)
    end
    dock_ring(output)
    pond_path(output)
    haunted_world(output)
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

  def relocating_npc_floor
    [[:home, :mother, 12, 7], [:shop, :oil_seller, 7, 5]].each do |map, key, x, y|
      Tidebound::World.travel(map, x - 1, y, 6)
      actor = Tidebound::World.actor(key)
      raise "NPC fixture is not present: #{key}" unless actor && !actor.through
      $game_player.move_right
      raise "Player walked into #{key}" unless $game_player.x == x - 1
      Tidebound::Scenes.run(actor, restore_positions: true) do
        actor.moveto(x, y + 1)
        $game_player.move_right
        unless [$game_player.x, $game_player.y] == [x, y]
          raise "Relocating #{key} left an invisible floor blocker"
        end
        $game_player.moveto(x, y)
      end
    end
    puts "PASS: NPC events block occupied cells and leave walkable floor after relocating"
  end

  def dock_ring(output)
    # Invisible native rail events must block the same perimeter as the ropes.
    [
      [65, 20, :move_right],
      [74, 20, :move_left],
      [69, 17, :move_down],
      [69, 24, :move_up]
    ].each do |x, y, move|
      Tidebound::World.travel(:docks, x, y)
      raise "Ring check requires normal collision" if $game_player.through
      $game_player.public_send(move)
      raise "Player crossed a ring rope" unless [$game_player.x, $game_player.y] == [x, y]
    end
    Tidebound::World.travel(:docks, 69, 24, 8)
    capture(output, "dock-ring")
    puts "PASS: native ring ropes block entry on every side; dock ring rendered"
  end

  def pond_path(output)
    path = load_data("NativePond.rxdata").fetch("hidden_path")
    Tidebound::World.travel(:road, 18, 58, 4)
    capture(output, "pond-path-entry")
    path[0...-1].each do |x, y|
      delta = [x - $game_player.x, y - $game_player.y]
      move = {
        [0, 1] => :move_down,
        [-1, 0] => :move_left,
        [1, 0] => :move_right,
        [0, -1] => :move_up
      }.fetch(delta)
      $game_player.public_send(move)
      unless [$game_player.x, $game_player.y] == [x, y]
        raise "Hidden pond path blocked at #{x},#{y}"
      end
      $game_player.moveto(x, y)
    end
    cache = $game_map.events.fetch(28)
    unless [cache.x, cache.y] == path.last && cache.tile_id > 0
      raise "Hidden pond reward has no visible marker at the end of the path"
    end
    $game_player.turn_left
    capture(output, "pond-path-cache")
    Tidebound::World.travel(:road, 20, 59, 2)
    capture(output, "pond-bank")
    Tidebound::World.travel(:road, 36, 73, 2)
    capture(output, "pond-south-trees")
    puts "PASS: native player follows the concealed pond trail to its visible cache; pond banks rendered"
  end

  def walk_to(x, y)
    start = [$game_player.x, $game_player.y]
    target = [x, y]
    rows = Tidebound::MAP_PASSAGES.fetch($game_map.map_id)
    queue = [start]
    previous = { start => nil }
    until queue.empty? || previous.key?(target)
      point = queue.shift
      [[0, 1], [-1, 0], [1, 0], [0, -1]].each do |dx, dy|
        cell = [point[0] + dx, point[1] + dy]
        if previous.key?(cell) || cell[0] < 0 || cell[1] < 0 || cell[1] >= rows.length ||
             cell[0] >= rows.first.length || rows[cell[1]][cell[0]] != "1"
          next
        end
        previous[cell] = point
        queue << cell
      end
    end
    raise "No returnable native route to #{target.inspect}" unless previous.key?(target)
    route = []
    point = target
    while previous[point]
      route.unshift(point)
      point = previous[point]
    end
    moves = {
      [0, 1] => :move_down,
      [-1, 0] => :move_left,
      [1, 0] => :move_right,
      [0, -1] => :move_up
    }
    route.each do |cell|
      delta = [cell[0] - $game_player.x, cell[1] - $game_player.y]
      $game_player.public_send(moves.fetch(delta))
      unless [$game_player.x, $game_player.y] == cell
        raise "Native trail blocked at #{cell.inspect}"
      end
      $game_player.moveto(*cell)
    end
  end

  def step_transfer(move, expected)
    $game_player.public_send(move)
    deadline = System.uptime + 10
    until [$game_map.map_id, $game_player.x, $game_player.y] == expected
      raise "Native threshold did not transfer to #{expected.inspect}" if System.uptime > deadline
      Graphics.update
      Input.update
      $scene.update
    end
    Graphics.transition(0)
  end

  def haunted_world(output)
    # Keep the unattended route deterministic; sample the real native tables below.
    encounter_disabled = $game_system.encounter_disabled
    $game_system.encounter_disabled = true
    Tidebound::World.travel(:forest, :north)
    step_transfer(:move_up, [117, 24, 52])
    capture(output, "haunted-forest")
    grass =
      $game_map.height.times.flat_map do |y|
        $game_map.width.times.filter_map do |x|
          [x, y] if $game_map.terrain_tag(x, y).land_wild_encounters
        end
      end
    raise "Haunted forest grass cannot generate encounters" if grass.empty?
    walk_to(*grass.first)
    unless $PokemonEncounters.encounter_type == :Land
      raise "Haunted forest has no native Land encounter"
    end
    walk_to(25, 14)
    Tidebound::World.camera_to(25, 10, 0)
    capture(output, "ancient-skull")
    Tidebound::World.camera_to(25, 14, 0)
    walk_to(25, 13)
    step_transfer(:move_up, [118, 24, 37])
    unless $PokemonEncounters.encounter_type == :Cave
      raise "Cave does not use native step encounters"
    end
    40.times do
      species, level = $PokemonEncounters.choose_wild_pokemon(:Cave)
      unless level >= 20 && GameData::Species.get(species).types.include?(:GHOST)
        raise "Skull cave generated a weak or non-Ghost encounter"
      end
    end
    capture(output, "skull-cave-mouth")
    walk_to(26, 9)
    capture(output, "skull-cave-deep")
    walk_to(24, 38)
    step_transfer(:move_down, [117, 25, 14])
    walk_to(24, 53)
    step_transfer(:move_down, [103, 17, 4])
    puts "PASS: native forest/skull/cave thresholds, walkable deep route and return; level 20+ Ghost encounters"
  ensure
    $game_system.encounter_disabled = encounter_disabled
  end

  def furniture_overhangs(output)
    # Exercise native player collision, including events and both ends of a step.
    # Starting just right of each object, walk across its northern cap.
    fixtures = [
      [:bed, :bedroom, 5, 4, 2],
      [:shelf, :bedroom, 13, 4, 2],
      [:cupboard, :bedroom, 10, 4, 2],
      [:plant, :bedroom, 13, 9, 1],
      [:shop_shelf, :shop, 6, 4, 3],
      [:damaged_machine, :hideout, 5, 4, 2],
      [:display_case, :vault, 10, 14, 2],
      [:trimmed_cupboard, :lantern, 5, 6, 2]
    ]
    fixtures.each do |name, map, x, y, width|
      Tidebound::World.travel(map, x, y, 4)
      raise "Furniture check requires normal collision" if $game_player.through
      width.times do
        $game_player.move_left
        x -= 1
        unless [$game_player.x, $game_player.y] == [x, y]
          raise "Cannot walk behind #{name} at #{x},#{y}"
        end
        # Finish interpolation before attempting the next normal movement.
        $game_player.moveto(x, y)
        $game_player.move_down
        raise "Walked into #{name} body" unless [$game_player.x, $game_player.y] == [x, y]
      end
      capture(output, "behind-#{name}")
    end
    puts "PASS: native player walks behind furniture overhangs and cannot enter their bodies"
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
