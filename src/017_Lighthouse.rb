# The beacon housing belongs to the map; only its lit lens is a runtime overlay.
# The glow shares the map viewport, scroll position and existing lamp quest flag.
class TideboundBeaconGlow < Sprite
  def initialize(map,viewport)
    super(viewport);@map=map
    self.bitmap=Bitmap.new('Graphics/Pictures/Tidebound_Beacon_Glow')
    self.z=90;update
  end
  def update
    super
    self.x=5*32-@map.display_x/Game_Map::X_SUBPIXELS
    self.y=2*32-@map.display_y/Game_Map::Y_SUBPIXELS
    self.visible=!!Tidebound::Opening.flags[:lamp_lit]
    self.opacity=235+(Math.sin(System.uptime*1.1)*12).to_i
  end
  def dispose;bitmap.dispose;super;end
end
EventHandlers.add(:on_new_spriteset_map,:tidebound_beacon,proc { |spriteset,viewport|
  spriteset.addUserSprite(TideboundBeaconGlow.new(spriteset.map,viewport)) if spriteset.map.map_id==104
})
