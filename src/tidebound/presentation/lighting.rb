# Screen-space illumination. RGBA uploads are native mkxp-z operations; the
# coarse light field never reads the game framebuffer or redraws world sprites.
module Tidebound::Lighting
  CELL = 4
  module_function

  def settings(map_id)
    Tidebound::World::MAP_SETTINGS[map_id]&.fetch(:lighting, nil)
  end

  def enabled?(map_id)
    config = settings(map_id)
    config && !config.empty?
  end

  # An explicitly activated item, not the brightest object merely owned.
  def active_item
    item = Tidebound.story[:light_item]
    return nil unless item && $bag && $bag.has?(item)
    ITEM_LIGHTS[item.to_s]
  end

  def toggle_item(item)
    return false unless ITEM_LIGHTS.key?(item.to_s) && $bag && $bag.has?(item)
    Tidebound.story[:light_item] = Tidebound.story[:light_item] == item.to_sym ? nil : item.to_sym
    true
  end

  def strength(source, now, phase, default = 0.7)
    pulse = Math.sin(now * 2.1 + phase) * 0.65 + Math.sin(now * 3.7 + phase) * 0.35
    [source.fetch("strength", default) * (1 + source.fetch("flicker", 0) * pulse), 1].min
  end

  def inside?(x, y, rect)
    x >= rect[0] && y >= rect[1] && x < rect[0] + rect[2] && y < rect[1] + rect[3]
  end

  # Open segment intersection: a wall's near face may be lit, its far side may not.
  def blocked?(sx, sy, x, y, blockers)
    blockers.any? do |left, top, width, height|
      near, far = 0.001, 0.999
      [
        [sx, x - sx, left, left + width],
        [sy, y - sy, top, top + height]
      ].each do |start, delta, lo, hi|
        if delta.abs < 0.00001
          far = -1 if start <= lo || start >= hi
        else
          a, b = [(lo - start) / delta.to_f, (hi - start) / delta.to_f].minmax
          near = [near, a].max
          far = [far, b].min
        end
      end
      far > near
    end
  end

  # One cached stencil per source. Moving lights invalidate only their own stencil.
  class Field
    attr_reader :width, :height
    def initialize(width, height, config)
      @width, @height, @config = width, height, config
      @cache = {}
      @profiles = {}
      count = width * height
      @illumination = Array.new(count, 0.0)
      @red, @green, @blue = Array.new(count, 0.0), Array.new(count, 0.0), Array.new(count, 0.0)
      @darkness = [2, 4, 9, 0] * count
      @warmth = [0, 0, 0, 255] * count
    end

    def ambient(y)
      base = @config.fetch("ambient", 60) / 100.0
      fade = @config["north_fade"]
      return base unless fade
      t = [[(fade["from_y"] - y / 32.0) / (fade["from_y"] - fade["to_y"]), 0].max, 1].min
      t = t * t * (3 - 2 * t)
      base + (fade["ambient"] / 100.0 - base) * t
    end

    # Cache radial falloff independently of position, so moving lights do not
    # repeat square roots for every field sample on every step.
    def profile(source)
      radius = source.fetch("radius", 3) * 32.0
      stretch = source.fetch("stretch", [1, 1])
      rx, ry = radius * stretch[0], radius * stretch[1]
      softness = source.fetch("softness", 0.8)
      @profiles[[rx, ry, softness]] ||= begin
        points = []
        (-ry.ceil.div(CELL)..ry.ceil.div(CELL)).each do |dy|
          (-rx.ceil.div(CELL)..rx.ceil.div(CELL)).each do |dx|
            distance = Math.sqrt((dx * CELL / rx)**2 + (dy * CELL / ry)**2)
            next if distance >= 1
            edge = [[(1 - distance) / softness, 0].max, 1].min
            points << [dx, dy, edge * edge * (3 - 2 * edge)]
          end
        end
        points
      end
    end

    def stencil(key, x, y, source)
      cx, cy = x.div(CELL), y.div(CELL)
      signature = [cx, cy, source]
      previous = @cache[key]
      return previous[1] if previous && previous[0] == signature
      bounds = source["bounds"] || @config["bounds"]
      blockers = @config.fetch("blockers", [])
      points =
        profile(source).filter_map do |dx, dy, weight|
          gx, gy = cx + dx, cy + dy
          px, py = (gx * CELL + CELL / 2.0) / 32, (gy * CELL + CELL / 2.0) / 32
          next if bounds && !Tidebound::Lighting.inside?(px, py, bounds)
          if !blockers.empty? && Tidebound::Lighting.blocked?(x / 32.0, y / 32.0, px, py, blockers)
            next
          end
          [gx, gy, weight]
        end
      @cache[key] = [signature, points]
      points
    end

    def render(origin_x, origin_y, sources)
      illumination = @illumination.fill(0.0)
      red, green, blue = @red.fill(0.0), @green.fill(0.0), @blue.fill(0.0)
      @cache.delete_if { |key, _| !sources.any? { |s| s[0] == key } }
      ox, oy = origin_x.div(CELL), origin_y.div(CELL)
      sources.each do |key, x, y, source, strength|
        radius = source.fetch("radius", 3) * 32.0
        stretch = source.fetch("stretch", [1, 1])
        if x + radius * stretch[0] < origin_x || x - radius * stretch[0] > origin_x + @width * CELL
          next
        end
        if y + radius * stretch[1] < origin_y || y - radius * stretch[1] > origin_y + @height * CELL
          next
        end
        color = source.fetch("color", [255, 255, 255])
        # Only the chromatic difference adds a faint tint; neutral visibility adds none.
        floor = color.min
        colored = color.max != floor
        tint = color.map { |c| (c - floor) * 0.12 }
        unobstructed = @config.fetch("blockers", []).empty?
        points = unobstructed ? profile(source) : stencil(key, x, y, source)
        dx, dy = unobstructed ? [x.div(CELL) - ox, y.div(CELL) - oy] : [-ox, -oy]
        bounds = unobstructed && (source["bounds"] || @config["bounds"])
        points.each do |gx, gy, weight|
          sx, sy = gx + dx, gy + dy
          next if sx < 0 || sy < 0 || sx >= @width || sy >= @height
          if bounds &&
               !Tidebound::Lighting.inside?(
                 ((sx + ox) * CELL + CELL / 2.0) / 32,
                 ((sy + oy) * CELL + CELL / 2.0) / 32,
                 bounds
               )
            next
          end
          index = sy * @width + sx
          amount = weight * strength
          illumination[index] = 1 - (1 - illumination[index]) * (1 - amount)
          if colored
            r, g, b = tint[0] * amount, tint[1] * amount, tint[2] * amount
            red[index] = r if r > red[index]
            green[index] = g if g > green[index]
            blue[index] = b if b > blue[index]
          end
        end
      end
      darkness, warmth = @darkness, @warmth
      @height.times do |y|
        base = ambient((oy + y) * CELL)
        @width.times do |x|
          index = y * @width + x
          brightness = base + (1 - base) * illumination[index]
          offset = index * 4
          darkness[offset + 3] = ((1 - brightness) * 255).round
          warmth[offset] = red[index].round
          warmth[offset + 1] = green[index].round
          warmth[offset + 2] = blue[index].round
        end
      end
      [darkness.pack("C*"), warmth.pack("C*")]
    end
  end

  class Renderer
    attr_reader :field, :last_render_ms
    def initialize(map)
      @map = map
      @config = Tidebound::Lighting.settings(map.map_id)
      @viewport = Viewport.new(0, 0, Graphics.width, Graphics.height)
      @viewport.z = 2
      @dark = Sprite.new(@viewport)
      @warm = Sprite.new(@viewport)
      @warm.blend_type = 1
      @warm.z = 1
      @signature = nil
      resize
      update
    end

    def resize
      @size = [Graphics.width, Graphics.height]
      @viewport.rect.set(0, 0, *@size)
      @field = Field.new(Graphics.width.div(CELL) + 2, Graphics.height.div(CELL) + 2, @config)
      [@dark, @warm].each do |sprite|
        sprite.bitmap.dispose if sprite.bitmap
        sprite.bitmap = Bitmap.new(@field.width, @field.height)
        sprite.zoom_x = sprite.zoom_y = CELL
      end
      @signature = nil
    end

    def sources(now, ox, oy)
      records = []
      @config
        .fetch("sources", [])
        .each_with_index do |source, index|
          flag = source["flag"]
          next if flag && !Tidebound.story[flag.to_sym]
          if source["event"]
            event = @map.events[source["event"]]
            next unless event && event.list && !event.transparent && event.opacity > 0
            x, y = event.screen_x + ox, event.screen_y + oy - 16
          else
            x, y = source.fetch("position").map { |v| v * 32 }
          end
          dx, dy = source.fetch("offset", [0, 0])
          power = Tidebound::Lighting.strength(source, now, index * 2.39)
          records << [index, x + dx, y + dy, source, power]
        end
      if @map.map_id == $game_map.map_id
        player = @config.fetch("player", {})
        x, y = $game_player.screen_x + ox, $game_player.screen_y + oy - 16
        records << [:player, x, y, player, Tidebound::Lighting.strength(player, now, 0, 0.35)]
        item = Tidebound::Lighting.active_item
        records << [:item, x, y, item, Tidebound::Lighting.strength(item, now, 1)] if item
      end
      records
    end

    def update
      return if disposed?
      # Connected maps can retain spritesets. Only the current map owns the screen mask.
      active = @map.map_id == $game_map.map_id
      @dark.visible = @warm.visible = active
      return unless active
      resize if @size != [Graphics.width, Graphics.height]
      ox = (@map.display_x / Game_Map::X_SUBPIXELS).round
      oy = (@map.display_y / Game_Map::Y_SUBPIXELS).round
      now = System.uptime
      lights = sources(now, ox, oy)
      signature = [
        ox.div(CELL),
        oy.div(CELL),
        lights.map { |k, x, y, s, p| [k, x.div(CELL), y.div(CELL), s, (p * 100).round] }
      ]
      # The bitmap scrolls every frame, even when its sampled field can be reused.
      [@dark, @warm].each do |sprite|
        sprite.x = -(ox % CELL) - $game_screen.shake
        sprite.y = -(oy % CELL)
      end
      return if signature == @signature
      started = System.uptime
      pixels = @field.render(ox, oy, lights)
      @dark.bitmap.raw_data = pixels[0]
      @warm.bitmap.raw_data = pixels[1]
      @last_render_ms = (System.uptime - started) * 1000
      @signature = signature
    end

    def disposed?
      !!@disposed
    end

    def dispose
      return if disposed?
      [@dark, @warm].each do |sprite|
        sprite.bitmap.dispose
        sprite.dispose
      end
      @viewport.dispose
      @disposed = true
    end
  end
end

EventHandlers.add(
  :on_new_spriteset_map,
  :tidebound_lighting,
  proc do |spriteset, _viewport|
    if Tidebound::Lighting.enabled?(spriteset.map.map_id)
      spriteset.addUserSprite(Tidebound::Lighting::Renderer.new(spriteset.map))
    end
  end
)

Tidebound::Lighting::ITEM_LIGHTS.each_key do |id|
  ItemHandlers::UseFromBag.add(id.to_sym, proc { |_item| next 2 })
  ItemHandlers::UseInField.add(
    id.to_sym,
    proc do |item|
      next false unless Tidebound::Lighting.toggle_item(item)
      pbMessage(
        (
          if Tidebound.story[:light_item]
            _INTL("You light the lantern.")
          else
            _INTL("You put out the lantern.")
          end
        )
      )
      next true
    end
  )
end
