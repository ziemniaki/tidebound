# Window light follows exact source glass pixels; never invents a new window frame.
module Tidebound::DockDetails
  module_function
  def window_tile?(id)
    x=(id-384)%8; y=(id-384)/8
    return false if id<384
    (y==230 && [2,3].include?(x)) || (y==232 && x==0) ||
      (y==231 && [6,7].include?(x)) || (y==233 && [4,5,6].include?(x)) ||
      (y==226 && x==5) || (x==6 && [447,448].include?(y))
  end
  def glass?(c, id)
    x=(id-384)%8; y=(id-384)/8
    return c.red==39 && c.green==47 && c.blue==87 if x==6 && [447,448].include?(y)
    # Native blue panes; grey frames, mullions, walls and door panels are excluded.
    c.alpha>0 && c.blue>=180 && c.green>c.red+25 && c.blue>c.green+25
  end
  def safe_dock_position
    return unless $game_map.map_id==112 && $game_player && !Tidebound::Opening.flags[:dock_revision]
    mask=Tidebound::MAP_PASSAGES[112];x=$game_player.x;y=$game_player.y
    occupied=$game_map.events.values.reject(&:through).map { |e| [e.x,e.y] }
    unless mask[y] && mask[y][x]=='1' && !occupied.include?([x,y])
      choices=[]
      mask.each_with_index { |row,yy| row.each_char.with_index { |v,xx| choices<<[xx,yy] if v=='1' && !occupied.include?([xx,yy]) } }
      spot=choices.min_by { |xx,yy| [(xx-x).abs+(yy-y).abs,yy,xx] }
      $game_player.moveto(*spot) if spot
    end
    Tidebound::Opening.flags[:dock_revision]=1
  end
end
class TideboundWindowPane < Sprite
  attr_reader :pane_pixels
  def initialize(map,x,y,id,atlas,viewport)
    super(viewport);@map=map;@tx=x;@ty=y
    self.bitmap=Bitmap.new(32,32)
    @pane_pixels=[]
    sx=((id-384)%8)*32;sy=((id-384)/8)*32
    32.times do |py|
      32.times do |px|
        c=atlas.get_pixel(sx+px,sy+py)
        next unless Tidebound::DockDetails.glass?(c,id)
        @pane_pixels<<[px,py]
        bright=c.green>165
        bitmap.set_pixel(px,py,bright ? Color.new(255,218,145,235) : Color.new(234,167,79,225))
      end
    end
    update
  end
  def update
    super
    self.x=(@tx*Game_Map::REAL_RES_X-@map.display_x)/Game_Map::X_SUBPIXELS
    self.y=(@ty*Game_Map::REAL_RES_Y-@map.display_y)/Game_Map::Y_SUBPIXELS
  end
  def dispose;bitmap.dispose;super;end
end
class TideboundWindowLights
  def disposed?; !!@disposed; end
  def initialize(map)
    @viewport=Viewport.new(0,0,Graphics.width,Graphics.height);@viewport.z=1
    @sprites=[]
    atlas=Bitmap.new('Graphics/Tilesets/'+map.tileset_name)
    map.height.times do |y|
      map.width.times do |x|
        id=map.data[x,y,1]
        next unless Tidebound::DockDetails.window_tile?(id)
        @sprites<<TideboundWindowPane.new(map,x,y,id,atlas,@viewport)
      end
    end
    atlas.dispose
  end
  def update;@sprites.each(&:update);end
  def dispose;@sprites.each(&:dispose);@viewport.dispose;@disposed=true;end
end
class TideboundQuayProp < Sprite
  def initialize(event,viewport)
    super(viewport);@event=event;self.bitmap=Bitmap.new(128,96);self.ox=32;self.oy=80
    self.ox=96 if event.name=='Dock boat' && event.x==24
    b=bitmap;wood=Color.new(125,96,68);dark=Color.new(52,57,56);rope=Color.new(167,150,111)
    case event.name
    when 'Dock bollard'
      b.fill_rect(22,63,20,15,dark);b.fill_rect(25,54,14,20,wood)
      [61,65,69].each { |y| b.fill_rect(22,y,20,2,rope) }
    when 'Dock nets'
      b.fill_rect(8,57,43,20,Color.new(38,58,59,180))
      7.times { |i| b.fill_rect(9+i*6,58,2,18,Color.new(115,132,118)) }
      5.times { |i| b.fill_rect(9,58+i*4,40,1,rope) }
      b.fill_rect(16,58,4,3,Color.new(202,197,156))
    when 'Dock boat'
      [ [8,57,93,17],[14,51,81,29],[21,47,67,36] ].each { |r| b.fill_rect(*r,dark) }
      b.fill_rect(21,51,66,28,wood);b.fill_rect(25,54,58,22,Color.new(69,63,53))
      [33,51,71].each { |x| b.fill_rect(x,53,5,24,Color.new(168,130,84)) }
      b.fill_rect(30,61,68,3,rope);b.fill_rect(93,58,11,9,wood)
      b.fill_rect(10,82,82,2,Color.new(93,127,139,80))
    when 'Dock stall'
      b.fill_rect(10,54,50,27,wood);b.fill_rect(8,50,54,7,rope)
      [15,51].each { |x| b.fill_rect(x,70,5,19,dark) }
      b.fill_rect(12,42,45,8,Color.new(72,94,88));b.fill_rect(12,47,45,2,Color.new(167,176,149))
    end
    update
  end
  def update
    super;self.x=@event.screen_x;self.y=@event.screen_y;self.z=@event.screen_z
  end
  def dispose;bitmap.dispose;super;end
end
EventHandlers.add(:on_new_spriteset_map,:tidebound_dock_details,proc { |spriteset,viewport|
  map=spriteset.map
  next unless [102,108,112].include?(map.map_id)
  spriteset.addUserSprite(TideboundWindowLights.new(map))
  if map.map_id==112
    Tidebound::DockDetails.safe_dock_position
    map.events.each_value { |e| spriteset.addUserSprite(TideboundQuayProp.new(e,viewport)) if ['Dock boat','Dock bollard','Dock nets','Dock stall'].include?(e.name) }
  end
})
