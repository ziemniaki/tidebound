module Tidebound::World
  MAP_IDS = MAPS.values.freeze
  module_function
  def perpetual_night?
    $game_map && MAP_SETTINGS[$game_map.map_id]&.fetch(:night)
  end
  def atmosphere
    settings = MAP_SETTINGS[$game_map.map_id]
    return unless settings
    $game_screen.start_tone_change(Tone.new(*settings.fetch(:tone)), 0)
    $game_map.fog_name = settings.fetch(:fog)
    $game_map.fog_opacity = settings.fetch(:opacity)
    $game_map.fog_zoom = 160
    $game_map.fog_sx = settings.fetch(:speed)
    $game_map.fog_sy = 0
    $game_map.fog_blend_type = 0
  end
end

# Passage masks belong only to the opening maps. Character collision,
# touch/action events and map bounds remain the engine's normal implementations.
module Tidebound::World::Passages
  def passable?(x, y, d, self_event = nil)
    mask = Tidebound::MAP_PASSAGES[@map_id]
    return super unless mask
    return valid?(x, y) && mask[y][x] == "1"
  end
  def playerPassable?(x, y, d, self_event = nil)
    return passable?(x, y, d, self_event) if Tidebound::MAP_PASSAGES[@map_id]
    super
  end
  def passableStrict?(x, y, d, self_event = nil)
    return passable?(x, y, d, self_event) if Tidebound::MAP_PASSAGES[@map_id]
    super
  end
  def terrain_tag(x, y, count_bridge = false)
    return GameData::TerrainTag.get(:None) if Tidebound::MAP_PASSAGES[@map_id]
    super
  end
end
Game_Map.prepend(Tidebound::World::Passages)

EventHandlers.add(
  :on_enter_map,
  :tidebound_atmosphere,
  proc { |_old_map_id| Tidebound::World.atmosphere }
)
# Loading a save does not always enter a new map.
EventHandlers.add(
  :on_new_spriteset_map,
  :tidebound_restore_tone,
  proc { |_spriteset, _viewport| Tidebound::World.atmosphere }
)

# Ordinary story locations stay night regardless of host time. Real timers still run.
module TideboundNightClock
  def isNight?(time = nil)
    return true if Tidebound::World.perpetual_night?
    super
  end
  %i[isDay? isMorning? isAfternoon? isEvening?].each do |name|
    define_method(name) do |time = nil|
      next false if Tidebound::World.perpetual_night?
      super(time)
    end
  end
  def getShade
    return 0 if Tidebound::World.perpetual_night?
    super
  end
end
PBDayNight.singleton_class.prepend(TideboundNightClock) if defined?(PBDayNight)
module TideboundNightBattle
  def prepare_battle(battle)
    super
    battle.time = 2 if Tidebound::World.perpetual_night?
  end
end
if defined?(BattleCreationHelperMethods)
  BattleCreationHelperMethods.singleton_class.prepend(TideboundNightBattle)
end
