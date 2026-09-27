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
    @fire = Tidebound::Actors.role(event) == "fire"
    load_prop(Tidebound::Actors.role(event))
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
    @key = Tidebound::Actors.role(event) == "keys"
    load_prop(Tidebound::Actors.role(event))
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
