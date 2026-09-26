# Authored pixel props use world coordinates and the same night tone as the map.
class TideboundDemoProp < Tidebound::Presentation::OwnedSprite
  def initialize(event,viewport)
    super(viewport);@event=event
    asset=event.name.split(':')[1]
    self.bitmap=Bitmap.new("Graphics/Pictures/Tidebound/Demo_#{asset}")
    self.ox=0;self.oy=0;update
  end
  def update
    super
    asset=@event.name.split(':')[1]
    dx,dy=asset.start_with?('ship') ? [2,-4] : [0,0]
    self.x=@event.screen_x-16+dx*32;self.y=@event.screen_y-32+dy*32
    self.z=1
  end
end
EventHandlers.add(:on_new_spriteset_map,:tidebound_demo_props,proc { |s,v|
  next unless s.map.map_id==112
  s.map.events.each_value do |event|
    s.addUserSprite(TideboundDemoProp.new(event,v)) if event.name.start_with?('Demo prop:')
  end
})
