# Temporary scene ownership. Story progress and inventory remain feature-owned.
module Tidebound::Scenes
  @owned = {}
  module_function

  def owns?(event)
    @owned.key?(event)
  end

  def run(*events, restore_positions: false)
    events = events.compact.uniq
    raise "Scene already owns an actor" if events.any? { |event| owns?(event) }
    saved =
      events.map do |event|
        [event, event.x, event.y, event.direction, event.through, event.opacity, event.move_speed]
      end
    camera = Tidebound::World.camera_target
    map_id = $game_map.map_id
    events.each { |event| @owned[event] = true }
    yield
  ensure
    if saved
      saved.each do |event, x, y, direction, through, opacity, speed|
        cancel_route(event)
        if restore_positions
          event.moveto(x, y)
          event.direction = direction
        end
        event.through = through
        event.opacity = opacity
        event.move_speed = speed
        @owned.delete(event)
      end
      Tidebound::World.camera_target = $game_map.map_id == map_id ? camera : nil
      Tidebound::Actors.refresh($game_map)
    end
  end

  # Essentials has no cancellation API. Restore the route it saved before forcing.
  def cancel_route(event)
    return unless event.move_route_forcing
    event.instance_variable_set(:@move_route, event.instance_variable_get(:@original_move_route))
    event.instance_variable_set(
      :@move_route_index,
      event.instance_variable_get(:@original_move_route_index)
    )
    event.instance_variable_set(:@original_move_route, nil)
    event.instance_variable_set(:@move_route_forcing, false)
    event.instance_variable_set(:@wait_count, 0)
    event.instance_variable_set(:@wait_start, nil)
  end
end
