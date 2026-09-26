# Stock Pokemon art is used deliberately as a temporary gameplay reference.
# Regional artwork is selected through each Pokemon's stored form.
class TideboundCompanionSprite < PokemonIconSprite
  def initialize(event, viewport)
    @map_event = event
    @house_species = event.name.match?(/^(House|Room):/) ? event.name.split(":").last.to_sym : nil
    @outside_dog = event.name == "Pookie outside"
    @house_species = :POOCHYENA if @outside_dog
    @spirit_index = event.name.start_with?("Spirit:") ? event.name.split(":").last.to_i : nil
    record = @spirit_index.nil? ? nil : Tidebound.state.souls[@spirit_index]
    original = @house_species ? Tidebound::Opening.household_pets[@house_species] : record&.pokemon
    wild_species = event.name.start_with?("Wild:") ? event.name.split(":")[1].to_sym : nil
    pokemon = original ? Tidebound.copy(original) : Pokemon.new(@house_species || wild_species || :NATU, 4)
    pokemon.heal
    super(pokemon, viewport)
    setOffset(PictureOrigin::BOTTOM)
    update
  end

  def update
    super
    if @spirit_index
      record = Tidebound.state.souls[@spirit_index]
      self.visible = !!(record && record.status == :waiting && Tidebound.state.realm == :astral)
      self.opacity = 165 + (Math.sin(System.uptime * 2) * 30).to_i
      self.color = Color.new(140, 188, 214, 100)
    elsif @house_species
      self.visible = !!Tidebound::Opening.household_pets[@house_species]
      if @outside_dog
        self.visible &&= [:not_started, :requested, :running, :at_pier].include?(Tidebound::Opening.flags[:walk_state])
      elsif @map_event.name == "Room:NATU"
        self.visible &&= Tidebound::Opening.flags[:walk_state] != :complete
        self.visible &&= Tidebound::DreamRoom.wick_visible? if @map_event.map_id == 115
      elsif @house_species != :MAKUHITA
        self.visible &&= Tidebound::Opening.flags[:walk_state] == :complete
      end
      self.opacity = 255
      self.opacity = Tidebound::DreamRoom.wick_alpha || 255 if @map_event.map_id == 115 && @house_species == :NATU
    else
      self.visible = @map_event.name.count(":") > 1 ? Tidebound::NeighborQuest.wild_visible?(@map_event.name) : !Tidebound::Opening.flags[:wood_bird_gone]
      self.opacity = 255
    end
    @map_event.through = !self.visible unless @map_event.move_route_forcing
    self.x = @map_event.screen_x
    self.y = @map_event.screen_y + (@spirit_index ? (Math.sin(System.uptime * 1.4) * 3).to_i : 0)
    self.z = @map_event.screen_z
  end
end

class TideboundLampSprite < Sprite
  def initialize(event, viewport)
    super(viewport)
    @map_event = event
    self.bitmap = Bitmap.new(64, 80)
    self.ox = 32
    self.oy = 64
    @fire = event.name == "Fire"
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
    self.x = @map_event.screen_x
    self.y = @map_event.screen_y
    self.z = @map_event.screen_z
    self.opacity = 230 + (Math.sin(System.uptime * (@fire ? 8 : 1.2)) * 20).to_i
    self.opacity = 145 if @map_event.name == "Main lamp" && !Tidebound::Opening.flags[:lamp_lit]
  end

  def dispose
    self.bitmap.dispose
    super
  end
end

class TideboundLaprasSprite < PokemonIconSprite
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
    self.visible = !!Tidebound::Opening.lapras_visible
    self.x = @map_event.screen_x
    self.y = @map_event.screen_y + (Math.sin(System.uptime) * 4).to_i
    self.z = @map_event.screen_z
    self.opacity = Tidebound::Opening.lapras_alpha.to_i
  end
  def dispose
    super
    @ghost_viewport.dispose
  end
end

EventHandlers.add(:on_new_spriteset_map, :tidebound_event_sprites,
  proc { |spriteset, viewport|
    next unless Tidebound::Opening::MAP_IDS.include?(spriteset.map.map_id)
    spriteset.addUserSprite(TideboundPookieFollowerSprite.new(viewport))
    spriteset.map.events.each_value do |event|
      sprite = case event.name
               when /^Spirit:/, /^Wild:/, /^House:/, /^Room:/, "Pookie outside" then TideboundCompanionSprite.new(event, viewport)
               when "Fire", "Main lamp", "Downward lamp", "Return", "Ashes"
                 TideboundLampSprite.new(event, viewport) unless event.name == "Main lamp" && spriteset.map.map_id == 104
               when /^Crate/, "Shop keys" then TideboundPropSprite.new(event, viewport)
               when "Lapras" then TideboundLaprasSprite.new(event, viewport)
               end
      spriteset.addUserSprite(sprite) if sprite
      spriteset.addUserSprite(TideboundSleepSprite.new(event, viewport)) if event.name == "Pookie outside"
    end
  }
)

class Scene_TideboundTitle
  def main
    viewport = Viewport.new(0, 0, Graphics.width, Graphics.height)
    viewport.z = 99999
    backdrop = Sprite.new(viewport)
    backdrop.bitmap = Bitmap.new(Graphics.width, Graphics.height)
    b = backdrop.bitmap
    b.fill_rect(0, 0, Graphics.width, Graphics.height, Color.new(12, 20, 30))
    b.fill_rect(0, 205, Graphics.width, Graphics.height - 205, Color.new(18, 34, 44))
    9.times { |i| b.fill_rect(0, 210 + i * 21, Graphics.width, 1, Color.new(24, 42, 52)) }
    b.fill_rect(368, 132, 26, 97, Color.new(31, 43, 50))
    b.fill_rect(362, 125, 38, 8, Color.new(44, 51, 55))
    b.fill_rect(371, 115, 20, 12, Color.new(232, 208, 156))
    b.fill_rect(365, 108, 32, 6, Color.new(62, 62, 59))
    pbSetSystemFont(b)
    b.font.size = 40
    b.font.color = Color.new(225, 220, 206)
    b.draw_text(42, 75, 320, 55, "TIDEBOUND")
    b.font.size = 20
    b.font.color = Color.new(159, 177, 182)
    b.draw_text(44, 129, 300, 32, "The keeper's light")
    b.font.size = 18
    b.draw_text(44, 320, 420, 32, "Press Enter")
    b.font.size = 14
    b.draw_text(44, 350, 400, 24, "Demo 1 | 0.8.0  |  An unofficial fan project")
    pbBGMPlay("Tidebound Shore", 80, 100)
    Graphics.transition(20)
    loop do
      Graphics.update
      Input.update
      break if Input.trigger?(Input::USE)
    end
    Graphics.freeze
    backdrop.bitmap.dispose
    backdrop.dispose
    viewport.dispose
    $scene = Scene_DebugIntro.new
  end
end

# A visual copy only: the household individual is never healed or rerolled here.
class TideboundPookieFollowerSprite < PokemonIconSprite
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
    self.visible = !!(follower && Tidebound::Opening.flags[:walk_state] == :following)
    return unless self.visible
    follower.opacity = 0 # Native movement/save object; our icon supplies its art.
    self.x = follower.screen_x
    self.y = follower.screen_y
    self.z = follower.screen_z
  end
end

class TideboundPropSprite < Sprite
  def initialize(event, viewport)
    super(viewport)
    @map_event = event
    self.bitmap = Bitmap.new(32, 32)
    self.ox = 16
    self.oy = 32
    @key = event.name == "Shop keys"
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
    self.x = @map_event.screen_x
    self.y = @map_event.screen_y
    self.z = @map_event.screen_z
    if @key
      self.visible = !Tidebound::Opening.flags[:keys_collected] && !Tidebound::Opening.flags[:shop_unlocked]
      @map_event.through = !self.visible
      self.opacity = 205 + (Math.sin(System.uptime * 3) * 50).to_i
    elsif !@map_event.move_route_forcing
      @map_event.through = false
    end
  end

  def dispose
    self.bitmap.dispose
    super
  end
end


class TideboundSleepSprite < Sprite
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
    self.visible = [:not_started, :requested].include?(Tidebound::Opening.flags[:walk_state])
    self.x = @map_event.screen_x + 5
    self.y = @map_event.screen_y - 42 + (Math.sin(System.uptime) * 2).to_i
    self.z = @map_event.screen_z + 1
  end
  def dispose
    self.bitmap.dispose
    super
  end
end

# Tiny native pixel props share the map's 32px grid and stock-art scale.
class TideboundCoastProp < Sprite
  def initialize(event, viewport)
    super(viewport)
    @map_event=event
    self.bitmap=Bitmap.new(48,64)
    self.ox=24;self.oy=48
    dark=Color.new(53,46,43);wood=Color.new(125,94,65)
    if event.name.start_with?("Coast lamp:")
      self.bitmap.fill_rect(6,4,36,36,Color.new(236,178,91,14))
      self.bitmap.fill_rect(12,10,24,24,Color.new(244,193,108,24))
      self.bitmap.fill_rect(22,22,4,25,dark)
      self.bitmap.fill_rect(16,12,16,17,dark)
      self.bitmap.fill_rect(19,15,10,11,Color.new(240,187,101))
      self.bitmap.fill_rect(22,16,4,8,Color.new(255,229,169))
      self.bitmap.fill_rect(14,10,20,3,wood)
      self.bitmap.fill_rect(20,46,8,2,wood)
    elsif event.name=="Sea glass"
      self.bitmap.fill_rect(20,42,8,4,Color.new(54,111,100))
      self.bitmap.fill_rect(22,40,6,3,Color.new(132,174,143))
      self.bitmap.fill_rect(22,40,2,2,Color.new(213,218,173))
    elsif event.name=="Tide bell"
      self.bitmap.fill_rect(12,16,4,31,wood)
      self.bitmap.fill_rect(32,16,4,31,wood)
      self.bitmap.fill_rect(10,14,28,4,dark)
      self.bitmap.fill_rect(22,18,4,6,dark)
      self.bitmap.fill_rect(18,24,12,10,Color.new(135,126,83))
      self.bitmap.fill_rect(16,33,16,3,Color.new(181,154,96))
    else
      self.bitmap.fill_rect(21,28,6,19,wood)
      self.bitmap.fill_rect(19,28,10,4,dark)
      3.times { |i| self.bitmap.fill_rect(18,36+i*3,13,2,Color.new(178,158,111)) }
      self.bitmap.fill_rect(29,41,2,14,Color.new(158,142,109))
    end
    update
  end
  def update
    super
    self.x=@map_event.screen_x;self.y=@map_event.screen_y;self.z=@map_event.screen_z
  end
  def dispose
    self.bitmap.dispose
    super
  end
end
