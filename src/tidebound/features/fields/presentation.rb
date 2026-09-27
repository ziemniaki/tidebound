# Tile-anchored cues: thresholds align with masonry, not character sprite feet.
class TideboundThreshold < Tidebound::Presentation::OwnedSprite
  def initialize(event, viewport, map)
    @cue_viewport = Viewport.new(0, 0, Graphics.width, Graphics.height)
    @cue_viewport.z = 1
    super(@cue_viewport, owns_viewport: true)
    @event = event
    @map = map
    self.bitmap = Bitmap.new(32, 32)
    self.ox = 0
    self.oy = 0
    cue = Tidebound::Actors.info(event)["cue"]
    north, east, west = cue == "north", cue == "east", cue == "west"
    # Outdoor house triggers on their facade tile use its bottom sill; the
    # lighthouse trigger is one tile below its facade and uses the TOP edge.
    cue_rect = east ? [28, 5, 3, 22] : west ? [1, 5, 3, 22] : north ? [5, 1, 22, 3] : [5, 27, 22, 3]
    bitmap.fill_rect(*cue_rect, Color.new(176, 166, 137))
    if east || west
      bitmap.fill_rect(cue_rect[0], 7, 1, 18, Color.new(218, 205, 167))
    else
      bitmap.fill_rect(7, cue_rect[1], 18, 1, Color.new(218, 205, 167))
    end
    self.opacity = 205
    self.z = 0
    update
  end
  def update
    super
    position_at_tile(@map, @event.x, @event.y)
  end
end

# A separate untinted viewport lets local amber light survive the fixed night tone.
# Kept below message/menu viewports, with very faint light spill over nearby tiles.
class TideboundWarmLight < Tidebound::Presentation::OwnedSprite
  def initialize(map, x, y)
    @light_viewport = Viewport.new(0, 0, Graphics.width, Graphics.height)
    @light_viewport.z = 1
    super(@light_viewport, owns_viewport: true)
    @map = map
    @tile_x = x
    @tile_y = y
    load_prop("warm_light")
    update
  end
  def update
    super
    position_at_tile(@map, @tile_x, @tile_y, dx: 16, dy: 32)
    self.opacity = 242 + (Math.sin(System.uptime * 1.3) * 10).to_i
  end
end
# Keep picked trees visibly unripe, including after save/load and regrowth.
class TideboundBerryVisual < Tidebound::Presentation::OwnedSprite
  def initialize(event, viewport, map_id)
    super(viewport)
    @event = event
    @map_id = map_id
    @last_ripe = nil
    update
  end
  def update
    super
    x, y = Tidebound::World.local_xy(@map_id, @event.x, @event.y)
    stamp = (Tidebound.state.story[:berry_picks] || {})[[@map_id, x, y]]
    ripe = !stamp || Time.now.to_i - stamp >= Tidebound::FieldDetails::BERRY_SECONDS
    return if ripe == @last_ripe
    ripe ? @event.turn_up : @event.turn_left
    @last_ripe = ripe
  end
end
EventHandlers.add(
  :on_new_spriteset_map,
  :tidebound_field_details,
  proc do |spriteset, viewport|
    map = spriteset.map
    next unless Tidebound::World::MAP_IDS.include?(map.map_id)
    map.events.each_value do |event|
      if Tidebound::Actors.role(event) == "berry"
        spriteset.addUserSprite(TideboundBerryVisual.new(event, viewport, map.map_id))
      end
      if Tidebound::Actors.info(event)["cue"]
        spriteset.addUserSprite(TideboundThreshold.new(event, viewport, map))
      end
      if %w[coast_lamp fire].include?(Tidebound::Actors.role(event))
        spriteset.addUserSprite(TideboundWarmLight.new(map, event.x, event.y))
      end
    end
  end
)
