# Exercise the same bootstrap used by `play --scenario`, inside the existing smoke launch.
module NativeDevelopmentScenarios
  module_function

  def run(output)
    load_data("NativeScenarios.rxdata").each do |spec|
      @expected, @entered = spec, false
      DevelopmentScenario.boot(spec)
      raise "Map callbacks did not see the scenario state" unless @entered
      @expected = nil
      map, x, y, direction = spec.fetch("arrival")
      unless [$game_map.map_id, $game_player.x, $game_player.y, $game_player.direction] ==
               [map, x, y, direction]
        raise "Scenario arrived at the wrong entrance: #{spec.fetch("id")}"
      end
      unless $player.party.map { |pet| [pet.species.to_s, pet.level] } ==
               spec
                 .fetch("party")
                 .map { |key|
                   record = spec.fetch("pokemon").fetch(key)
                   [record.fetch("species").split("_").first, record.fetch("level")]
                 }
        raise "Scenario party differs from declaration"
      end
      spec
        .fetch("bag")
        .each do |item, count|
          raise "Scenario bag was not seeded" unless $bag.quantity(item.to_sym) == count
        end
      $scene.createSpritesets
      Graphics.transition(0)
      NativeScenarios.capture(output, "scenario-#{spec.fetch("id").tr("/", "-")}")
      interrupt_route if spec.fetch("id") == "neighbor/meal"
      profile(output) if spec.fetch("id") == "opening/docks"
      identity = $player.party.map { |pet| [Tidebound.identity(pet), pet.item_id] }
      story = Marshal.dump(Tidebound.story)
      raise "Scenario save failed" unless Game.save
      $scene.dispose
      SaveData.mark_values_as_unloaded
      saved = SaveData.get_data_from_file(SaveData::FILE_PATH)
      if spec.fetch("id") == "vault/visit"
        # A save from before repacking has a stale native map revision and tiles.
        saved[:game_system].magic_number = $data_system.magic_number ^ 1
        # Game.set_up_system loads this boot value before Game.load on launch.
        $game_system = saved[:game_system]
        original_tile = $game_map.data[0, 0, 0]
        saved[:map_factory].map.data[0, 0, 0] = original_tile + 1
      end
      Game.load(saved)
      if original_tile && $game_map.data[0, 0, 0] != original_tile
        raise "Existing save retained map tiles from before the atlas rebuild"
      end
      unless identity == $player.party.map { |pet| [Tidebound.identity(pet), pet.item_id] } &&
               Marshal.dump(Tidebound.story) == story
        raise "Scenario save/load lost identity, held items or quest state"
      end
      $scene = nil
    end
    puts "PASS: declared scenarios initialize before map callbacks and roundtrip native saves"
  ensure
    $scene.dispose if $scene.is_a?(Scene_Map) && $scene.map_renderer
  end

  def entered
    return unless @expected
    expected = DevelopmentScenario.story_value(@expected.fetch("story"))
    unless expected.all? { |key, value| Tidebound.story[key] == value } &&
             $player.party.length == @expected.fetch("party").length
      raise "Map entry observed incomplete scenario state"
    end
    @entered = true
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

  def profile(output)
    samples = []
    180.times do
      Input.update
      start = System.uptime
      $scene.update
      samples << (System.uptime - start) * 1000
      Graphics.update
    end
    samples.sort!
    report = {
      "map" => $game_map.map_id,
      "events" => $game_map.events.length,
      "frames" => samples.length,
      "update_p50_ms" => samples[samples.length / 2],
      "update_p95_ms" => samples[(samples.length * 0.95).floor],
      "update_max_ms" => samples.last
    }
    File.binwrite(File.join(output, "scene-profile.rxdata"), Marshal.dump(report))
    puts "Docks update profile (render pacing excluded): #{report.inspect}"
  end
end

EventHandlers.add(:on_enter_map, :native_scenario_seed, proc { NativeDevelopmentScenarios.entered })
