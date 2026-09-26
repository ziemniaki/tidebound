# Small field improvements. Additive state; no save-schema or pet-identity changes.
module Tidebound::FieldDetails
  FIRE_SECONDS = 15 * 60
  BERRY_SECONDS = 60 * 60
  EXITS = ['Door', 'Shop door', 'Forest path', 'South path', 'Bedroom exit', 'Storehouse door', 'Cellar stairs', 'Vault doorway', 'Dock city', 'Museum door'].freeze
  module_function

  def remaining(key, now = Time.now.to_i)
    last = (Tidebound.state.story[:fire_rests] || {})[key]
    return 0 unless last
    [[FIRE_SECONDS - (now - last), 0].max, FIRE_SECONDS].min
  end

  def heal_fire(key, now = Time.now.to_i)
    raise Tidebound::TransitionError, 'Fire belongs to the living world' unless Tidebound.state.realm == :living
    return false if remaining(key, now) > 0
    party = $player.party.reject { |p| p.egg? || Tidebound.borrowed?(p) }
    return false if party.empty?
    party.each do |p|
      p.hp = p.totalhp
      p.moves.each { |move| move.pp = move.total_pp }
    end
    (Tidebound.state.story[:fire_rests] ||= {})[key] = now
    true
  end

  def rest(key, checkpoint)
    Tidebound.state.checkpoint = checkpoint
    if heal_fire(key)
      pbMessage('You settle beside the fire. Your companions recover their HP and PP.')
      pbMessage('They can recover here again in 15 minutes. Poison and other conditions remain.')
    elsif $player.party.empty?
      pbMessage('You warm your hands beside the fire.')
    else
      minutes = (remaining(key) / 60.0).ceil
      pbMessage("You warm your hands. Your companions need another #{minutes} minute#{minutes == 1 ? '' : 's'} before this fire can restore them again.")
    end
  end

  def berry(map, x, y, item)
    key = [map, x, y]
    times = (Tidebound.state.story[:berry_picks] ||= {})
    now = Time.now.to_i
    if times[key] && now - times[key] < BERRY_SECONDS
      pbMessage('Only unripe berries remain. Let them grow a little longer.')
      return
    end
    return unless pbConfirmMessage("Ripe #{GameData::Item.get(item).name_plural} hang among the leaves. Pick two?")
    times[key] = now if pbReceiveItem(item, 2)
  end
end

# The generated maps override terrain globally; restore Grass only for its visible tile.
module Tidebound::FieldTerrain
  def terrain_tag(x, y, count_bridge = false)
    if [103,108].include?(@map_id) && valid?(x,y) && data[x,y,1] == 391
      return GameData::TerrainTag.get(:Grass)
    end
    super
  end
end
Game_Map.prepend(Tidebound::FieldTerrain)

# Route native grass encounters (including any double encounter) through the same
# pre-cleanup loss snapshot as the explicitly visible wild Pokemon.
module Tidebound::GrassBattles
  def start(*args, can_override: false)
    if can_override && [103,108].include?($game_map.map_id) && Tidebound.state.realm == :living
      result = Tidebound::Opening.fight(*args)
      return result == :astral ? 2 : result
    end
    super
  end
end
WildBattle.singleton_class.prepend(Tidebound::GrassBattles)

# Tile-anchored cues: thresholds align with masonry, not character sprite feet.
class TideboundThreshold < Sprite
  attr_reader :tile_anchor, :cue_rect
  def initialize(event, viewport, map)
    @cue_viewport=Viewport.new(0,0,Graphics.width,Graphics.height)
    @cue_viewport.z=1
    super(@cue_viewport)
    @event=event;@map=map
    @tile_anchor=[event.x,event.y]
    self.bitmap=Bitmap.new(32,32);self.ox=0;self.oy=0
    north=(map.map_id==102 && ['Door','Forest path'].include?(event.name)) ||
      (map.map_id==108 && event.name=='Door') || event.name=='Vault doorway'
    east=event.name=='Dock city'
    west=map.map_id==112 && event.name=='Door'
    # Outdoor house triggers on their facade tile use its bottom sill; the
    # lighthouse trigger is one tile below its facade and uses the TOP edge.
    @cue_rect=east ? [28,5,3,22] : west ? [1,5,3,22] : north ? [5,1,22,3] : [5,27,22,3]
    bitmap.fill_rect(*@cue_rect,Color.new(176,166,137))
    if east || west
      bitmap.fill_rect(@cue_rect[0],7,1,18,Color.new(218,205,167))
    else
      bitmap.fill_rect(7,@cue_rect[1],18,1,Color.new(218,205,167))
    end
    self.opacity=205;self.z=0
    update
  end
  def update
    super
    self.x=(@event.x*Game_Map::REAL_RES_X-@map.display_x)/Game_Map::X_SUBPIXELS
    self.y=(@event.y*Game_Map::REAL_RES_Y-@map.display_y)/Game_Map::Y_SUBPIXELS
  end
  def dispose;bitmap.dispose;super;@cue_viewport.dispose;end
end

# A separate untinted viewport lets local amber light survive the fixed night tone.
# Kept below message/menu viewports, with very faint light spill over nearby tiles.
class TideboundWarmLight < Sprite
  def initialize(map, x, y)
    @light_viewport=Viewport.new(0,0,Graphics.width,Graphics.height)
    @light_viewport.z=1
    super(@light_viewport)
    @map=map; @tile_x=x; @tile_y=y
    self.bitmap=Bitmap.new(128,128);self.ox=64;self.oy=88
    [60,50,40,30,20].each do |r|
      (-r..r).step(2) do |yy|
        half=Math.sqrt(r*r-yy*yy).to_i
        bitmap.fill_rect(64-half,64+yy,half*2,2,Color.new(255,174,71,5))
      end
    end
    bitmap.fill_rect(60,59,8,11,Color.new(255,207,121))
    bitmap.fill_rect(62,61,4,7,Color.new(255,239,186))
    update
  end
  def update
    super
    self.x=(@tile_x*Game_Map::REAL_RES_X-@map.display_x)/Game_Map::X_SUBPIXELS+16
    self.y=(@tile_y*Game_Map::REAL_RES_Y-@map.display_y)/Game_Map::Y_SUBPIXELS+32
    self.opacity=242+(Math.sin(System.uptime*1.3)*10).to_i
  end
  def dispose
    bitmap.dispose
    super
    @light_viewport.dispose
  end
end
# Keep picked trees visibly unripe, including after save/load and regrowth.
class TideboundBerryVisual < Sprite
  def initialize(event, viewport, map_id)
    super(viewport)
    @event=event; @map_id=map_id; @last_ripe=nil
    update
  end
  def update
    super
    x=@event.x; y=@event.y
    x-=24; y-=20 if @map_id==102
    stamp=(Tidebound.state.story[:berry_picks] || {})[[@map_id,x,y]]
    ripe=!stamp || Time.now.to_i-stamp>=Tidebound::FieldDetails::BERRY_SECONDS
    return if ripe==@last_ripe
    ripe ? @event.turn_up : @event.turn_left
    @last_ripe=ripe
  end
end
EventHandlers.add(:on_new_spriteset_map, :tidebound_field_details, proc { |spriteset, viewport|
  map=spriteset.map
  next unless Tidebound::Opening::MAP_IDS.include?(map.map_id)
  map.events.each_value do |event|
    spriteset.addUserSprite(TideboundBerryVisual.new(event,viewport,map.map_id)) if event.name.start_with?('Berry:')
    spriteset.addUserSprite(TideboundThreshold.new(event,viewport,map)) if Tidebound::FieldDetails::EXITS.include?(event.name)
    if event.name.start_with?('Coast lamp:') || event.name=='Fire'
      spriteset.addUserSprite(TideboundWarmLight.new(map,event.x,event.y))
    end
  end

})
