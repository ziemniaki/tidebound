module Tidebound::World
  MAP_IDS = MAPS.values.freeze
  module_function
  def perpetual_night?
    $game_map && MAP_SETTINGS[$game_map.map_id]&.fetch(:night)
  end
  def perpetual_day?
    $game_map && MAP_SETTINGS[$game_map.map_id]&.fetch(:day, false)
  end
  def atmosphere
    settings = MAP_SETTINGS[$game_map.map_id]
    return unless settings
    lighting = settings.fetch(:lighting, {})
    tone = lighting.empty? ? settings.fetch(:tone) : lighting.fetch("tone", [0, 0, 0, 60])
    $game_screen.start_tone_change(Tone.new(*tone), 0)
    fog = settings.fetch(:fog)
    # CoastalMist owns the moving layers above local darkness; avoid a second veil.
    $game_map.fog_name = fog == "coastal_mist" ? "" : fog
    $game_map.fog_opacity = settings.fetch(:opacity)
    $game_map.fog_zoom = 160
    $game_map.fog_sx = settings.fetch(:speed)
    $game_map.fog_sy = 0
    $game_map.fog_blend_type = 0
  end
end

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
    return false if Tidebound::World.perpetual_day?
    super
  end
  def isDay?(time = nil)
    return false if Tidebound::World.perpetual_night?
    return true if Tidebound::World.perpetual_day?
    super
  end
  %i[isMorning? isAfternoon? isEvening?].each do |name|
    define_method(name) do |time = nil|
      next false if Tidebound::World.perpetual_night?
      next(name == :isAfternoon?) if Tidebound::World.perpetual_day?
      super(time)
    end
  end
  def getShade
    return 0 if Tidebound::World.perpetual_night?
    return 255 if Tidebound::World.perpetual_day?
    super
  end
  def getTone
    return Tone.new(0, 0, 0, 0) if Tidebound::World.perpetual_day?
    super
  end
end
PBDayNight.singleton_class.prepend(TideboundNightClock) if defined?(PBDayNight)
module TideboundNightBattle
  def prepare_battle(battle)
    super
    battle.time = 2 if Tidebound::World.perpetual_night?
    battle.time = 0 if Tidebound::World.perpetual_day?
  end
end
if defined?(BattleCreationHelperMethods)
  BattleCreationHelperMethods.singleton_class.prepend(TideboundNightBattle)
end
