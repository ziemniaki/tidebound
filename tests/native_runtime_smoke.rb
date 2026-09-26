# TEST ONLY: replaces Main in an isolated copy of a packaged Mac or Windows game.
# The Windows runtime omits the JSON library; Python converts this Marshal report.
report = ENV.fetch("TIDEBOUND_SMOKE_REPORT")
begin
  puts "Smoke working directory: #{Dir.pwd}; animations on disk: #{File.exist?('Data/Animations.rxdata')}"
  raise "player smoke unexpectedly started in debug mode" if $DEBUG
  MessageTypes.load_default_messages if FileTest.exist?("Data/messages_core.dat")
  PluginManager.runPlugins
  Compiler.main
  Game.initialize
  Game.set_up_system
  raise "unexpected Ruby version" unless RUBY_VERSION.start_with?("3.1.")
  $player = Player.new("Build smoke", :POKEMONTRAINER_Red)
  pokemon = Pokemon.new(:NATU, 7, $player)
  pokemon.item = :MYSTICWATER
  state = Tidebound::State.new
  identity = state.assign_identity(pokemon)
  state.enter_astral!([pokemon], { :map_id => 103, :x => 17, :y => 25 })
  state.begin_encounter!(identity)
  recovered = state.recover!(identity)
  save_path = File.join(System.data_directory, "smoke-save.rxdata")
  raise "save path fell back to the game directory" unless SaveData::FILE_PATH.start_with?(System.data_directory + "/")
  File.binwrite(save_path, Marshal.dump([state, recovered]))
  saved_state, saved_pokemon = Marshal.load(File.binread(save_path))
  raise "native save identity changed" unless Tidebound.identity(saved_pokemon) == identity
  raise "native save lost held item" unless saved_pokemon.item_id == :MYSTICWATER
  raise "native save lost state" unless saved_state.realm == :astral
  bitmap = Bitmap.new(320, 96)
  bitmap.font.name = "Power Green"
  bitmap.font.size = 24
  bitmap.draw_text(0, 0, 320, 48, "Tidebound native build check")
  sprite = Sprite.new
  sprite.bitmap = bitmap
  Graphics.transition(0)
  10.times { Graphics.update; Input.update }
  shot = Graphics.snap_to_bitmap
  shot.to_file(ENV.fetch("TIDEBOUND_SMOKE_SCREENSHOT"))
  shot.dispose
  sprite.dispose
  bitmap.dispose
  File.binwrite(report, Marshal.dump({
    "passed" => true, "ruby" => RUBY_VERSION, "ruby_platform" => RUBY_PLATFORM,
    "version" => Tidebound::VERSION, "save_directory" => System.data_directory,
    "game_directory" => Dir.pwd, "game_directory_writable" => File.writable?(Dir.pwd),
    "checks" => ["load engine and custom scripts", "compiled data", "native Pokemon/state save roundtrip",
                "graphics/font rendering", "input initialization"]
  }))
rescue Exception => error
  File.binwrite(report, Marshal.dump({ "passed" => false, "error" => error.full_message }))
end
exit
