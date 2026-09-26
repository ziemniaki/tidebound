# TEST ONLY: replaces Main in an isolated copy of a packaged Mac or Windows game.
require "json"
report = ENV.fetch("TIDEBOUND_SMOKE_REPORT")
begin
  puts "Smoke working directory: #{Dir.pwd}; animations on disk: #{File.exist?('Data/Animations.rxdata')}"
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
  File.binwrite("smoke-save.rxdata", Marshal.dump([state, recovered]))
  saved_state, saved_pokemon = Marshal.load(File.binread("smoke-save.rxdata"))
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
  File.write(report, JSON.pretty_generate({
    :passed => true, :ruby => RUBY_VERSION, :ruby_platform => RUBY_PLATFORM,
    :version => Tidebound::VERSION, :save_directory => System.data_directory,
    :checks => ["load engine and custom scripts", "compiled data", "native Pokemon/state save roundtrip",
                "graphics/font rendering", "input initialization"]
  }))
rescue Exception => error
  File.write(report, JSON.pretty_generate({ :passed => false, :error => error.full_message }))
end
exit
