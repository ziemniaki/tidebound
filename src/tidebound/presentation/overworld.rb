# Stock Pokemon art is used deliberately as a temporary gameplay reference.
# Regional artwork is selected through each Pokemon's stored form.
class TideboundCompanionSprite < PokemonIconSprite
  include Tidebound::Presentation::Position
  def initialize(event, viewport)
    @map_event = event
    actor = @actor = Tidebound::Actors.info(event)
    @house_species =
      %w[house room outside_dog].include?(actor["role"]) ? actor.fetch("species").to_sym : nil
    @spirit_index = actor["index"]
    record = @spirit_index.nil? ? nil : Tidebound.state.souls[@spirit_index]
    original = @house_species ? Tidebound::Opening.household_pets[@house_species] : record&.pokemon
    wild_species = actor["species"]&.to_sym
    pokemon =
      original ? Tidebound.copy(original) : Pokemon.new(@house_species || wild_species || :NATU, 4)
    pokemon.heal
    super(pokemon, viewport)
    setOffset(PictureOrigin::BOTTOM)
    update
  end

  def update
    super
    self.visible = Tidebound::Actors.visible?(@map_event, @actor)
    if @spirit_index
      self.opacity = 165 + (Math.sin(System.uptime * 2) * 30).to_i
      self.color = Color.new(140, 188, 214, 100)
    else
      self.opacity = 255
      self.opacity = Tidebound::DreamRoom.wick_alpha || 255 if @map_event.map_id == 115 &&
        @house_species == :NATU
    end
    self.x = @map_event.screen_x
    self.y = @map_event.screen_y + (@spirit_index ? (Math.sin(System.uptime * 1.4) * 3).to_i : 0)
    self.z = @map_event.screen_z
  end
end

class TideboundLampSprite < Tidebound::Presentation::OwnedSprite
  def initialize(event, viewport)
    super(viewport)
    @map_event = event
    self.bitmap = Bitmap.new(64, 80)
    self.ox = 32
    self.oy = 64
    @fire = Tidebound::Actors.role(event) == "fire"
    if @fire
      self.bitmap.fill_rect(14, 51, 34, 6, Color.new(69, 51, 44))
      self.bitmap.fill_rect(22, 47, 30, 6, Color.new(98, 63, 41))
      self.bitmap.fill_rect(23, 26, 19, 26, Color.new(189, 87, 42))
      self.bitmap.fill_rect(28, 17, 10, 32, Color.new(224, 147, 68))
      self.bitmap.fill_rect(31, 34, 7, 17, Color.new(255, 220, 139))
    else
      self.bitmap.fill_rect(29, 20, 6, 40, Color.new(66, 68, 77))
      self.bitmap.fill_rect(20, 16, 24, 22, Color.new(150, 122, 77))
      self.bitmap.fill_rect(23, 19, 18, 16, Color.new(249, 212, 138))
      self.bitmap.fill_rect(19, 14, 26, 4, Color.new(80, 80, 90))
      self.bitmap.fill_rect(24, 60, 16, 4, Color.new(72, 74, 80))
    end
    update
  end

  def update
    super
    position_at_event(@map_event)
    self.opacity = 230 + (Math.sin(System.uptime * (@fire ? 8 : 1.2)) * 20).to_i
    self.opacity = 145 if Tidebound::Actors.role(@map_event) == "main_lamp" &&
      !Tidebound.story[:lamp_lit]
  end
end

class TideboundLaprasSprite < PokemonIconSprite
  include Tidebound::Presentation::Position
  def initialize(event, viewport)
    @map_event = event
    # Like the local lamps, its faint light survives the map's strong night tint.
    # This sea-only apparition remains below message/menu viewports.
    @ghost_viewport = Viewport.new(0, 0, Graphics.width, Graphics.height)
    @ghost_viewport.z = 1
    super(Pokemon.new(:LAPRAS_1, 10), @ghost_viewport)
    setOffset(PictureOrigin::BOTTOM)
    self.zoom_x = 2
    self.zoom_y = 2
    self.color = Color.new(0, 0, 0, 0)
    update
  end
  def update
    super
    self.visible = !!Tidebound::SeaGlimpse.visible
    self.x = @map_event.screen_x
    self.y = @map_event.screen_y + (Math.sin(System.uptime) * 4).to_i
    self.z = @map_event.screen_z
    self.opacity = Tidebound::SeaGlimpse.alpha.to_i
  end
  def dispose
    super
    @ghost_viewport.dispose unless @ghost_viewport.disposed?
  end
end

EventHandlers.add(
  :on_new_spriteset_map,
  :tidebound_event_sprites,
  proc do |spriteset, viewport|
    next unless Tidebound::World::MAP_IDS.include?(spriteset.map.map_id)
    spriteset.addUserSprite(TideboundPookieFollowerSprite.new(viewport))
    spriteset.map.events.each_value do |event|
      sprite =
        case Tidebound::Actors.role(event)
        when "spirit", "wood_bird", "neighbor_wild", "shore_duck", "house", "room", "outside_dog"
          TideboundCompanionSprite.new(event, viewport)
        when "fire", "main_lamp", "lamp"
          unless Tidebound::Actors.role(event) == "main_lamp" && spriteset.map.map_id == 104
            TideboundLampSprite.new(event, viewport)
          end
        when "crate", "keys"
          TideboundPropSprite.new(event, viewport)
        when "lapras"
          TideboundLaprasSprite.new(event, viewport)
        end
      spriteset.addUserSprite(sprite) if sprite
      if Tidebound::Actors.role(event) == "outside_dog"
        spriteset.addUserSprite(TideboundSleepSprite.new(event, viewport))
      end
    end
  end
)

# A visual copy only: the household individual is never healed or rerolled here.
class TideboundPookieFollowerSprite < PokemonIconSprite
  include Tidebound::Presentation::Position
  def initialize(viewport)
    original = Tidebound::Opening.household_pets[:POOCHYENA]
    pokemon = original ? Tidebound.copy(original) : Pokemon.new(:POOCHYENA, 7)
    pokemon.heal
    super(pokemon, viewport)
    setOffset(PictureOrigin::BOTTOM)
    update
  end

  def update
    super
    follower = Followers.get(Tidebound::Opening::POOKIE_FOLLOWER)
    self.visible = !!(follower && Tidebound.story[:walk_state] == :following)
    return unless self.visible
    follower.opacity = 0 # Native movement/save object; our icon supplies its art.
    position_at_event(follower)
  end
end

class TideboundPropSprite < Tidebound::Presentation::OwnedSprite
  def initialize(event, viewport)
    super(viewport)
    @map_event = event
    self.bitmap = Bitmap.new(32, 32)
    self.ox = 16
    self.oy = 32
    @key = Tidebound::Actors.role(event) == "keys"
    if @key
      gold = Color.new(232, 204, 130)
      self.bitmap.fill_rect(10, 8, 8, 8, gold)
      self.bitmap.fill_rect(12, 10, 4, 4, Color.new(68, 67, 59))
      self.bitmap.fill_rect(13, 16, 3, 11, gold)
      self.bitmap.fill_rect(16, 22, 4, 3, gold)
    else
      self.bitmap.fill_rect(2, 7, 28, 24, Color.new(66, 43, 31))
      self.bitmap.fill_rect(4, 9, 24, 20, Color.new(144, 104, 64))
      [13, 20, 27].each { |y| self.bitmap.fill_rect(4, y, 24, 2, Color.new(88, 60, 42)) }
      [7, 23].each { |x| self.bitmap.fill_rect(x, 9, 3, 20, Color.new(185, 142, 88)) }
    end
    update
  end

  def update
    super
    position_at_event(@map_event)
    if @key
      self.visible = Tidebound::Actors.visible?(@map_event)
      self.opacity = 205 + (Math.sin(System.uptime * 3) * 50).to_i
    end
  end
end

class TideboundSleepSprite < Tidebound::Presentation::OwnedSprite
  def initialize(event, viewport)
    super(viewport)
    @map_event = event
    self.bitmap = Bitmap.new(32, 32)
    pbSetSmallFont(self.bitmap)
    self.bitmap.font.color = Color.new(234, 232, 218)
    self.bitmap.draw_text(0, 0, 32, 32, "z")
  end
  def update
    super
    self.visible = %i[not_started requested].include?(Tidebound.story[:walk_state])
    self.x = @map_event.screen_x + 5
    self.y = @map_event.screen_y - 42 + (Math.sin(System.uptime) * 2).to_i
    self.z = @map_event.screen_z + 1
  end
end

# Tiny native pixel props share the map's 32px grid and stock-art scale.
class TideboundCoastProp < Tidebound::Presentation::OwnedSprite
  def initialize(event, viewport)
    super(viewport)
    @map_event = event
    self.bitmap = Bitmap.new(48, 64)
    self.ox = 24
    self.oy = 48
    dark = Color.new(53, 46, 43)
    wood = Color.new(125, 94, 65)
    if Tidebound::Actors.role(event) == "coast_lamp"
      self.bitmap.fill_rect(6, 4, 36, 36, Color.new(236, 178, 91, 14))
      self.bitmap.fill_rect(12, 10, 24, 24, Color.new(244, 193, 108, 24))
      self.bitmap.fill_rect(22, 22, 4, 25, dark)
      self.bitmap.fill_rect(16, 12, 16, 17, dark)
      self.bitmap.fill_rect(19, 15, 10, 11, Color.new(240, 187, 101))
      self.bitmap.fill_rect(22, 16, 4, 8, Color.new(255, 229, 169))
      self.bitmap.fill_rect(14, 10, 20, 3, wood)
      self.bitmap.fill_rect(20, 46, 8, 2, wood)
    elsif Tidebound::Actors.role(event) == "sea_glass"
      self.bitmap.fill_rect(20, 42, 8, 4, Color.new(54, 111, 100))
      self.bitmap.fill_rect(22, 40, 6, 3, Color.new(132, 174, 143))
      self.bitmap.fill_rect(22, 40, 2, 2, Color.new(213, 218, 173))
    elsif Tidebound::Actors.role(event) == "tide_bell"
      self.bitmap.fill_rect(12, 16, 4, 31, wood)
      self.bitmap.fill_rect(32, 16, 4, 31, wood)
      self.bitmap.fill_rect(10, 14, 28, 4, dark)
      self.bitmap.fill_rect(22, 18, 4, 6, dark)
      self.bitmap.fill_rect(18, 24, 12, 10, Color.new(135, 126, 83))
      self.bitmap.fill_rect(16, 33, 16, 3, Color.new(181, 154, 96))
    else
      self.bitmap.fill_rect(21, 28, 6, 19, wood)
      self.bitmap.fill_rect(19, 28, 10, 4, dark)
      3.times { |i| self.bitmap.fill_rect(18, 36 + i * 3, 13, 2, Color.new(178, 158, 111)) }
      self.bitmap.fill_rect(29, 41, 2, 14, Color.new(158, 142, 109))
    end
    update
  end
  def update
    super
    position_at_event(@map_event)
  end
end

EventHandlers.add(
  :on_new_spriteset_map,
  :tidebound_coast_props,
  proc do |spriteset, viewport|
    next unless [102, 108, 110, 112].include?(spriteset.map.map_id)
    spriteset.map.events.each_value do |event|
      unless Tidebound::Actors.role(event) == "coast_lamp" ||
               %w[sea_glass tide_bell mooring_rope].include?(Tidebound::Actors.role(event))
        next
      end
      spriteset.addUserSprite(TideboundCoastProp.new(event, viewport))
    end
  end
)
