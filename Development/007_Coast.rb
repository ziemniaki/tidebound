# Coast layout helpers and additive save migration. Native travel stays native.
module Tidebound
  module Opening
    COAST_OFFSET = [24, 20].freeze
    POOKIE_PIER = [53, 20].freeze
    class << self
      attr_accessor :coast_camera_target, :lapras_alpha
    end
    module_function
    def coast_xy(x, y)
      [x + COAST_OFFSET[0], y + COAST_OFFSET[1]]
    end
    def travel_coast(x, y, direction = 2)
      travel(102, *coast_xy(x, y), direction)
    end
    def safe_coast_position(x, y)
      candidates = []
      Tidebound::MAP_PASSAGES[102].each_with_index do |row, yy|
        row.each_char.with_index do |cell, xx|
          next unless cell == "1"
          next if $game_map.events.values.any? { |e| e.x == xx && e.y == yy && !e.through && e.character_name != "" }
          candidates << [((xx-x).abs + (yy-y).abs), xx, yy]
        end
      end
      result = candidates.min
      result ? result[1, 2] : coast_xy(8, 16)
    end
    def migrate_coast!
      return unless flags[:opening_started]
      return if flags[:coast_revision].to_i >= 5
      $PokemonGlobal.followers.each do |data|
        next unless data.current_map_id == 102
        data.x += COAST_OFFSET[0]
        data.y += COAST_OFFSET[1]
      end
      $game_temp.followers = nil
      if $game_map.map_id == 102
        $game_player.moveto(*safe_coast_position(*coast_xy($game_player.x, $game_player.y)))
        $PokemonGlobal.followers.each do |data|
          next unless data.current_map_id == 102
          mask = Tidebound::MAP_PASSAGES[102]
          next if mask[data.y] && mask[data.y][data.x] == "1"
          data.x, data.y = $game_player.x, $game_player.y
        end
      end
      flags[:coast_revision] = 5
    end
    def camera_position(x, y)
      w = Graphics.width.to_f / Game_Map::TILE_WIDTH
      h = Graphics.height.to_f / Game_Map::TILE_HEIGHT
      [ [[x-w/2+0.5,0].max,$game_map.width-w].min*Game_Map::REAL_RES_X,
        [[y-h/2+0.5,0].max,$game_map.height-h].min*Game_Map::REAL_RES_Y ]
    end
    def coast_camera_to(x, y, duration = 0.65)
      start_x, start_y = $game_map.display_x, $game_map.display_y
      target_x, target_y = camera_position(x, y)
      pbWait(duration) do |elapsed|
        t = [elapsed/duration, 1.0].min; t = t*t*(3-2*t)
        $game_map.display_x = start_x+(target_x-start_x)*t
        $game_map.display_y = start_y+(target_y-start_y)*t
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
      blend = 1.0 - Math.exp(-6.0/[Graphics.frame_rate,1].max)
      $game_map.display_x += (x-$game_map.display_x)*blend
      $game_map.display_y += (y-$game_map.display_y)*blend
    end
    def lapras_scene
      pbMessage("The rope draws tight.\nThere is no boat at the end of it.")
      pbBGMFade(0.5)
      coast_camera_to(*coast_xy(55,22))
      pbWait(0.65)
      self.lapras_alpha = 0
      self.lapras_visible = true
      pbWait(0.9) { |elapsed| self.lapras_alpha = (145*[elapsed/0.9,1.0].min).to_i }
      self.lapras_alpha = 145
      pbMessage("Something pale rises through the dark water.")
      pbMessage("A face. Turned towards the lighthouse, as if waiting for its light.")
      pbWait(0.65)
      pbMessage("The sea goes on behind it. Farther than you can see.")
      pbWait(1.0) { |elapsed| self.lapras_alpha = (145*[1.0-elapsed,0].max).to_i }
      self.lapras_visible = false
      pbWait(0.4)
      flags[:lapras_glimpsed] = true
      pbMessage("Only the rope is moving now.")
    ensure
      self.lapras_visible = false
      self.lapras_alpha = 0
      coast_camera_home if $game_map.map_id == 102
      pbBGMPlay("Tidebound Shore",80,100)
    end
  end
end
EventHandlers.add(:on_frame_update,:tidebound_coast_camera,
  proc { Tidebound::Opening.coast_camera_frame })
EventHandlers.add(:on_new_spriteset_map,:tidebound_coast_props,
  proc { |spriteset,viewport|
    next unless [102,108,110,112].include?(spriteset.map.map_id)
    spriteset.map.events.each_value do |event|
      next unless event.name.start_with?("Coast lamp:") || ["Sea glass","Tide bell","Mooring rope"].include?(event.name)
      spriteset.addUserSprite(TideboundCoastProp.new(event,viewport))
    end
  })
