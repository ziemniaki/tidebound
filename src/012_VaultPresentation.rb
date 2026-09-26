# Native-size temporary pixel props. No supernatural effects on the public sabre.
class TideboundArchiveProp < Sprite
  def initialize(event, viewport)
    super(viewport);@event=event
    self.bitmap=Bitmap.new(96,112);self.ox=48;self.oy=104
    b=bitmap;iron=Color.new(67,78,82);edge=Color.new(115,124,123)
    wood=Color.new(110,77,50);dark=Color.new(31,40,45)
    if event.name=='Vault ironwork'
      b.fill_rect(4,4,88,104,Color.new(70,73,69))
      b.fill_rect(10,10,76,94,edge);b.fill_rect(16,16,64,88,dark)
      b.fill_rect(20,18,40,84,iron)
      [24,52,82].each { |y| b.fill_rect(20,y,40,4,edge) }
      [26,53].each { |x| [22,48,78,96].each { |y| b.fill_rect(x,y,3,3,Color.new(154,151,125)) } }
      b.fill_rect(35,47,13,25,Color.new(142,130,96));b.fill_rect(39,52,5,15,iron)
    elsif event.name=='Vault pillar'
      b.fill_rect(31,24,34,80,Color.new(105,106,97));b.fill_rect(35,29,25,67,Color.new(139,138,122))
      [24,53,78,99].each { |y| b.fill_rect(29,y,38,4,Color.new(84,91,87)) }
    elsif event.name=='Necklace drawer'
      b.fill_rect(24,64,48,40,dark);b.fill_rect(26,65,44,35,wood)
      [68,81,94].each { |y| b.fill_rect(28,y,40,2,Color.new(66,50,40));b.fill_rect(45,y+5,6,2,Color.new(201,177,112)) }
    else
      b.fill_rect(18,77,60,27,wood);b.fill_rect(21,60,54,26,Color.new(115,147,151))
      b.fill_rect(24,63,48,19,Color.new(41,69,77));b.fill_rect(23,61,49,2,Color.new(204,223,214))
      b.fill_rect(25,83,46,3,Color.new(192,172,124));b.fill_rect(42,94,12,4,Color.new(223,214,181))
      if event.name=='Sabre exhibit'
        b.fill_rect(31,72,8,4,Color.new(116,72,48));b.fill_rect(39,68,3,12,Color.new(208,178,102))
        b.fill_rect(42,72,21,3,Color.new(199,219,220));b.fill_rect(61,70,5,3,Color.new(218,231,227))
        b.fill_rect(44,71,16,1,Color.new(239,239,216))
      else
        b.fill_rect(39,69,16,9,Color.new(165,147,108));b.fill_rect(43,67,8,2,Color.new(210,194,148))
      end
    end
    update
  end
  def update
    super;self.x=@event.screen_x;self.y=@event.screen_y;self.z=@event.screen_z
  end
  def dispose;bitmap.dispose;super;end
end
EventHandlers.add(:on_new_spriteset_map,:tidebound_archive_props,proc { |spriteset,viewport|
  spriteset.map.events.each_value do |e|
    if ['Vault ironwork','Vault pillar','Necklace drawer','Sabre exhibit'].include?(e.name) || e.name.start_with?('Museum case:')
      spriteset.addUserSprite(TideboundArchiveProp.new(e,viewport))
    end
  end
})
