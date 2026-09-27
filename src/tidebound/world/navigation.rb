# Shared engine operations. Features own their story transitions.
module Tidebound::World
  class << self
    attr_accessor :coast_camera_target
  end
  module_function
  def erase_autorun
    pbMapInterpreter&.get_self&.erase
  end

  def travel(map_id, x, y, direction = 2)
    map_id = MAPS.fetch(map_id) if map_id.is_a?(Symbol)
    pbFadeOutIn do
      $game_temp.player_new_map_id = map_id
      $game_temp.player_new_x = x
      $game_temp.player_new_y = y
      $game_temp.player_new_direction = direction
      $scene.transfer_player
      $game_map.refresh
    end
  end

  def actor(key)
    location = ACTORS.fetch(key)
    return nil unless $game_map.map_id == location.fetch("map")
    $game_map.events[location.fetch("event")]
  end

  # Essentials' pbMoveRoute schedules a route; its wait argument does not wait.

  def animate(event, commands)
    return unless event
    previous_through = event.through
    pbMoveRoute(event, commands)
    deadline = System.uptime + 20
    while event.move_route_forcing
      raise "Tidebound: scene movement timed out" if System.uptime > deadline
      pbWait(0.025)
    end
    # Essentials appends THROUGH_OFF even for actors which were already through.
    event.through = previous_through
  end

  def local_xy(map_id, x, y)
    ox, oy = MAP_SETTINGS.fetch(map_id).fetch(:origin)
    [x - ox, y - oy]
  end
  def coast_xy(x, y)
    ox, oy = MAP_SETTINGS.fetch(MAPS.fetch(:coast)).fetch(:origin)
    [x + ox, y + oy]
  end
  def travel_coast(x, y, direction = 2)
    travel(:coast, *coast_xy(x, y), direction)
  end
  def camera_position(x, y)
    w = Graphics.width.to_f / Game_Map::TILE_WIDTH
    h = Graphics.height.to_f / Game_Map::TILE_HEIGHT
    [
      [[x - w / 2 + 0.5, 0].max, $game_map.width - w].min * Game_Map::REAL_RES_X,
      [[y - h / 2 + 0.5, 0].max, $game_map.height - h].min * Game_Map::REAL_RES_Y
    ]
  end
  def coast_camera_to(x, y, duration = 0.65)
    start_x, start_y = $game_map.display_x, $game_map.display_y
    target_x, target_y = camera_position(x, y)
    pbWait(duration) do |elapsed|
      t = [elapsed / duration, 1.0].min
      t = t * t * (3 - 2 * t)
      $game_map.display_x = start_x + (target_x - start_x) * t
      $game_map.display_y = start_y + (target_y - start_y) * t
    end
    $game_map.display_x, $game_map.display_y = target_x, target_y
  end
  def coast_camera_home
    coast_camera_to($game_player.x, $game_player.y)
  end
  def coast_camera_frame
    event = self.coast_camera_target
    return unless event && $game_map.map_id == 102
    x, y = camera_position(event.x, event.y)
    blend = 1.0 - Math.exp(-6.0 / [Graphics.frame_rate, 1].max)
    $game_map.display_x += (x - $game_map.display_x) * blend
    $game_map.display_y += (y - $game_map.display_y) * blend
  end
end
EventHandlers.add(
  :on_frame_update,
  :tidebound_coast_camera,
  proc { Tidebound::World.coast_camera_frame }
)
