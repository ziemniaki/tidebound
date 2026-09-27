# IDs and map ownership match generated data; labels deliberately do not.
def world_events(map_id)
  events = { 1 => OpeningEvent.new }
  (Tidebound::World::ACTOR_SETTINGS[map_id] || {}).each do |id, _info|
    events[id] = OpeningEvent.new("Fixture label #{id}", id)
  end
  events.each_value { |event| event.map_id = map_id }
  events
end

# Real Essentials Pokemon, bag and SaveData; graphics/movement have fixtures here.
def check(value, label)
  raise label unless value
end
def new_opening
  SaveData.mark_values_as_unloaded
  $quest_outcome = 1
  $quest_reject_item = nil
  $hideout_plays = 0
  $hideout_result = true
  $messages.clear
  $choices.clear
  $game_map = Game_Map.new
  $game_map.map_id = 107
  $game_map.events = world_events($game_map.map_id)
  $game_player = OpeningPlayerLocation.new
  $opening_interpreter = Interpreter.allocate
  $opening_interpreter.instance_variable_set(:@event_id, 1)
  $PokemonGlobal = OpeningGlobal.new
  $scene = OpeningScene.new
  $bag = PokemonBag.new
  $player = Player.new("Unnamed", :POKEMONTRAINER_Red)
  $tidebound = Tidebound::State.new
  $stats = Struct.new(:distance_walked).new(0)
  Followers.remove("Tidebound Pookie")
  Tidebound::Opening.begin_story
end
def walk_step_fixture
  $stats.distance_walked += 1
  Tidebound::Opening.walk_step
end

def roundtrip
  saved = Marshal.load(Marshal.dump(SaveData.compile_save_hash))
  $tidebound = nil
  $player = nil
  $bag = nil
  SaveData.mark_values_as_unloaded
  SaveData.load_all_values(saved)
end
def walk(pier = false)
  o = Tidebound::Opening
  o.bedroom_pet
  o.bedroom_exit
  o.home_arrival
  Tidebound::World.travel_coast(8, 16)
  o.pookie
  if pier
    $game_player.moveto(*Tidebound::World.coast_xy(34, 20))
    walk_step_fixture
    o.pier_run
    check(Tidebound.story[:walk_state] == :at_pier, "dog didn't run")
    before = Tidebound.story[:walk_steps]
    10.times { walk_step_fixture }
    check(Tidebound.story[:walk_steps] == before, "unaccompanied steps count")
    roundtrip
    Tidebound::World.travel(:home, 10, 12)
    o.home_arrival
    check(Tidebound.story[:walk_state] == :at_pier, "left dog at pier")
    Tidebound::World.travel_coast(44, 20)
    o.pookie
  end
  $game_player.moveto(*Tidebound::World.coast_xy(8, 18))
  (99 - Tidebound.story[:walk_steps]).times { walk_step_fixture }
  Tidebound::World.travel(:home, 10, 12)
  o.home_arrival
  check(Tidebound.story[:walk_state] == :following, "walk completed at 99")
  5.times { walk_step_fixture }
  check(Tidebound.story[:walk_steps] == 99, "indoor steps count")
  Tidebound::World.travel_coast(8, 18)
  walk_step_fixture
  check(Tidebound.story[:walk_steps] == 100, "100th step missing")
  roundtrip
  Tidebound::World.travel(:home, 10, 12)
  o.home_arrival
  check(
    Tidebound.story[:walk_state] == :complete && !Followers.get(o::POOKIE_FOLLOWER),
    "home completion/follower cleanup"
  )
end
