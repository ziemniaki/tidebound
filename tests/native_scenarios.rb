# Loaded only by the disposable native fixture, before its Main driver.
module NativeScenarios
  module_function

  def run(scenario, output)
    species if [:species, :all].include?(scenario)
    world(output) if [:world, :all].include?(scenario)
  end

  def species_snapshot
    # Essentials adds non-evolving :None family links on base species for forms.
    # Compare actual evolution rules; those compiler-only links cannot evolve.
    result = {}
    GameData::Species.each do |record|
      next unless [:WURMPLE, :SUNKERN, :EKANS, :ARBOK, :PSYDUCK, :FROSTCOON,
                   :GLACIVERM, :NIVALORA, :MOONKERN, :MOONFLORA, :WHYDUCK].include?(record.species)
      result[record.id] = [record.types, record.base_stats, record.abilities,
                           record.hidden_abilities, record.moves,
                           record.evolutions.reject { |entry| entry[1] == :None }.sort_by(&:to_s)]
    end
    result
  end

  def species
    expected = species_snapshot
    sources = Dir.glob('NativePBS/pokemon*.txt').map { |path| File.expand_path(path) }
    raise 'Species scenario requires PBS inputs' if sources.empty?
    # The shipped Linux tree is read-only. Compile into the isolated save area.
    destination = File.join(System.data_directory, 'pbs-check')
    Dir.mkdir(destination)
    Dir.mkdir(File.join(destination, 'Data'))
    Dir.chdir(destination) do
      Compiler.compile_pokemon(*sources.reject { |path| path =~ /pokemon_(forms|metrics)/ })
      Compiler.compile_pokemon_forms(*sources.select { |path| path.include?('pokemon_forms') })
    end
    actual = species_snapshot
    changed = (expected.keys | actual.keys).select { |key| expected[key] != actual[key] }
    raise "PBS compiler changed species: #{changed.map { |key| [key, expected[key], actual[key]] }.inspect}" unless changed.empty?
    [:GLACIVERM, :FROSTCOON, :NIVALORA, :MOONKERN, :MOONFLORA, :WHYDUCK].each do |species|
      pokemon = Pokemon.new(species, 20, $player)
      [false, true].each do |shiny|
        pokemon.shiny = shiny
        [false, true].each do |back|
          image = GameData::Species.sprite_bitmap_from_pokemon(pokemon, back)
          raise "Missing art: #{species}" unless image && image.bitmap.width > 0
          image.dispose
        end
      end
    end
    puts 'PASS: native PBS compiler agrees with generated species; front/back/shiny assets load'
  end

  def capture(output, name)
    12.times { Graphics.update; Input.update; $scene.updateSpritesets }
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
    scenes = { home: [10, 8], coast: [34, 36], forest: [17, 25],
               lantern: [6, 6], vault: [12, 10], docks: [18, 18], road: [30, 55] }
    Graphics.transition(0)
    scenes.each do |name, (x, y)|
      Tidebound::World.travel(name, x, y)
      capture(output, name)
    end
    save_path = File.join(System.data_directory, 'world-current.rxdata')
    raise 'Fresh world save failed' unless Game.save(save_path)
    bytes = File.binread(save_path)
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file(save_path))
    raise 'Current world save changed during load' unless File.binread(save_path) == bytes
    raise 'Current world save lost party' unless $player.party.first.species == :NATU
    puts 'PASS: fresh current world scenes and real Game.save/Game.load roundtrip'
  ensure
    $scene.dispose if $scene.is_a?(Scene_Map) && $scene.map_renderer
  end
end
