# A short, self-contained New Game scene. No avatar swap, encounters or save migration.
module Tidebound::BirdPrelude
  START=[1,9].freeze
  GOAL=[15,2].freeze
  TILE=24
  ORIGIN=[52,54].freeze
  ROUTES=[
    [[1,9],[5,9],[5,7],[3,7],[3,5],[9,5],[9,3],[13,3],[13,5],[15,5],[15,2]],
    [[1,9],[1,6]],[[3,5],[3,2],[6,2]],[[7,5],[7,8],[10,8],[10,6]],[[11,3],[11,1]]
  ].freeze
  CELLS={}
  ROUTES.each do |route|
    route.each_cons(2) do |a,b|
      x,y=a;dx=b[0]<=>x;dy=b[1]<=>y
      loop do
        CELLS[[x,y]]=true;break if [x,y]==b
        x+=dx;y+=dy
      end
    end
  end
  CELLS.freeze
  module_function
  def screen(cell);[ORIGIN[0]+cell[0]*TILE+TILE/2,ORIGIN[1]+cell[1]*TILE+TILE/2];end
  def passable?(cell);!!CELLS[cell];end
end

class Scene_TideboundBirdPrelude
  attr_reader :phase,:cell
  def initialize(return_scene)
    @return_scene=return_scene;@phase=:sleep;@cell=Tidebound::BirdPrelude::START.dup
    @sprites=[];@bitmaps=[];@time=0.0;@finished=false;@position=Tidebound::BirdPrelude.screen(@cell)
  end
  def bitmap(w,h);b=Bitmap.new(w,h);@bitmaps<<b;b;end
  def source(path);b=Bitmap.new(path);@bitmaps<<b;b;end
  def sprite(b,z=0)
    s=Sprite.new(@viewport);s.bitmap=b;s.z=z;@sprites<<s;s
  end
  def main
    build
    pbBGMPlay('Tidebound Stillness',65,80)
    Graphics.transition(16);@last_time=System.uptime
    until @finished
      Graphics.update;Input.update;update
    end
    Tidebound::Opening.flags[:bird_prelude_seen]=true
    Graphics.freeze
    $game_map.autoplay
    $scene=@return_scene
  ensure
    @sprites.reverse_each { |s|s.dispose unless s.disposed? }
    @bitmaps.reverse_each { |b|b.dispose unless b.disposed? }
    @viewport&.dispose
  end
  def build
    @viewport=Viewport.new(0,0,Graphics.width,Graphics.height);@viewport.z=99999
    background=bitmap(Graphics.width,Graphics.height);background.fill_rect(0,0,Graphics.width,Graphics.height,Color.new(2,4,8));sprite(background)
    floor=bitmap(Graphics.width,Graphics.height)
    Tidebound::BirdPrelude::CELLS.each_key do |cell|
      x,y=Tidebound::BirdPrelude.screen(cell)
      floor.fill_rect(x-12,y-12,24,24,Color.new(16,22,29))
      floor.fill_rect(x-9,y-9,18,18,Color.new(20,27,34))
      [[1,0],[-1,0],[0,1],[0,-1]].each do |dx,dy|
        next if Tidebound::BirdPrelude.passable?([cell[0]+dx,cell[1]+dy])
        floor.fill_rect(x+(dx<0 ? -12 : dx>0 ? 11 : -12),y+(dy<0 ? -12 : dy>0 ? 11 : -12),dx==0 ? 24 : 1,dy==0 ? 24 : 1,Color.new(43,48,54,190))
      end
    end
    @floor=sprite(floor,1);@floor.opacity=0
    # Blurred halo and wisps use layered translucent rectangles, keeping native pixel silhouettes crisp.
    halo=bitmap(120,100)
    15.times do |i|
      inset=i*3;halo.fill_rect(inset,inset,120-inset*2,100-inset*2,Color.new(71,84,98,4+i*2))
    end
    @halo=sprite(halo,2);@halo.ox=60;@halo.oy=50
    interior=source('Graphics/Tilesets/Interior general')
    trainer=source('Graphics/Characters/trainer_POKEMONTRAINER_Red')
    bed=bitmap(64,80);bed.blt(7,8,interior,Rect.new(24,4828,50,68))
    # The familiar child's head rests on the pillow; native blanket covers the body.
    bed.blt(20,13,trainer,Rect.new(4,3,24,20))
    bed.fill_rect(24,29,3,1,Color.new(63,47,46));bed.fill_rect(33,29,3,1,Color.new(63,47,46))
    @bed=sprite(bed,4);@bed.x=404;@bed.y=29;@bed.ox=12
    @bed.tone=Tone.new(-60,-64,-60,140);@bed.opacity=0
    icon=source('Graphics/Pokemon/Icons/NATU')
    @open_eye=bitmap(64,64);@open_eye.blt(0,0,icon,Rect.new(0,0,64,64))
    @closed_eye=bitmap(64,64);@closed_eye.blt(0,0,@open_eye,Rect.new(0,0,64,64))
    @closed_eye.fill_rect(27,38,5,6,@open_eye.get_pixel(25,38))
    @closed_eye.fill_rect(27,41,5,1,Color.new(44,54,53))
    @echo=sprite(@open_eye,5);@echo.ox=31;@echo.oy=43;@echo.tone=Tone.new(-55,-50,-30,220);@echo.opacity=0
    @bird=sprite(@closed_eye,6);@bird.ox=31;@bird.oy=43
    @bird.tone=Tone.new(-18,-28,-18,125)
    @mist=[]
    5.times do |n|
      b=bitmap(240,62)
      # Soft Gaussian wisps: visible on black, slow enough to keep paths legible.
      (0...62).step(2) do |y|
        (0...240).step(4) do |x|
          a=(Math.exp(-((x-120)/84.0)**2-((y-31)/19.0)**2)*64).to_i
          b.fill_rect(x,y,4,2,Color.new(57+n*3,64+n*3,75+n*3,a)) if a>0
        end
      end
      s=sprite(b,8);s.x=n*135-120;s.y=68+n*52;s.opacity=105;@mist<<s
    end
    words=bitmap(Graphics.width,86);pbSetSystemFont(words);words.font.size=24;words.font.color=Color.new(190,193,190)
    words.draw_text(0,8,Graphics.width,36,'A bird wants to play...',1)
    words.font.size=20
    words.draw_text(0,43,Graphics.width,36,'Take it for a little walk, 100 steps.',1)
    @words=sprite(words,10);@words.y=249;@words.opacity=0
    hint=bitmap(Graphics.width,30);pbSetSystemFont(hint);hint.font.size=17;hint.font.color=Color.new(123,133,144)
    hint.draw_text(0,0,Graphics.width,28,'Arrow keys: guide the bird.',1)
    @hint=sprite(hint,10);@hint.y=348;@hint.opacity=0
    black=bitmap(Graphics.width,Graphics.height);black.fill_rect(0,0,Graphics.width,Graphics.height,Color.new(0,0,0))
    @black=sprite(black,20);@black.opacity=0
    @bird.x=256;@bird.y=190;@bird.zoom_x=@bird.zoom_y=2
  end
  def update
    now=System.uptime;dt=[[now-@last_time,0.001].max,0.1].min;@last_time=now;@time+=dt
    if @time<1.8
      @phase=:sleep;@bird.zoom_y=2+Math.sin(@time*3)*0.035
    elsif @time<3.0
      @phase=:eye;@bird.bitmap=@open_eye;@bird.zoom_y=2
    elsif @time<5.8
      @phase=:caption;@words.opacity=[(@time-3)*210,255].min.to_i
    elsif @phase!=:moving && @phase!=:arrival
      @phase=:moving;@game_started=@time
    end
    if @phase==:moving
      reveal=[(@time-@game_started)/1.2,1].min
      @floor.opacity=(reveal*255).to_i;@bed.opacity=(reveal*205).to_i
      @words.opacity=((1-reveal)*255).to_i
      @hint.opacity=(@time-@game_started<8 ? reveal*180 : [180-(@time-@game_started-8)*90,0].max).to_i
      if reveal>=1
        advance(dt)
      else
        start=Tidebound::BirdPrelude.screen(@cell)
        @position=[256+(start[0]-256)*reveal,190+(start[1]-190)*reveal]
      end
      @bird.zoom_x=@bird.zoom_y=2-reveal
      @bird.x=@position[0];@bird.y=@position[1]+Math.sin(@time*4)*0.7
    elsif @phase==:arrival
      elapsed=@time-@arrival_time
      @bird.y=@position[1]-[elapsed*7,7].min
      @bird.bitmap=@closed_eye if elapsed>0.65
      @hint.opacity=0;@black.opacity=([[elapsed-0.8,0].max/1.1,1].min*255).to_i
      @finished=true if elapsed>=2.0
    end
    @halo.x=@bird.x;@halo.y=@bird.y;@halo.opacity=@phase==:moving ? 160 : 65
    @bed.zoom_y=1+Math.sin(@time*1.7)*0.005
    @mist.each_with_index do |s,i|
      s.x=((@time*(3+i)*0.65+i*135)%800)-220
      s.y=66+i*52+Math.sin(@time*0.3+i)*8
    end
  end
  def advance(dt)
    if @motion
      @motion[:t]+=dt;v=[@motion[:t]/0.15,1].min;v=v*v*(3-2*v)
      a=@motion[:from];b=@motion[:to]
      @position=[a[0]+(b[0]-a[0])*v,a[1]+(b[1]-a[1])*v]
      @echo.x=a[0];@echo.y=a[1];@echo.opacity=((1-v)*45).to_i
      if @motion[:t]>=0.15
        @cell=@motion[:cell];@motion=nil
        if @cell==Tidebound::BirdPrelude::GOAL
          @phase=:arrival;@arrival_time=@time
        end
      end
      return
    end
    direction=Input.dir4
    delta={2=>[0,1],4=>[-1,0],6=>[1,0],8=>[0,-1]}[direction]
    return unless delta
    candidate=[@cell[0]+delta[0],@cell[1]+delta[1]]
    return unless Tidebound::BirdPrelude.passable?(candidate)
    @bird.mirror=direction==6 if [4,6].include?(direction)
    @motion={from:Tidebound::BirdPrelude.screen(@cell),to:Tidebound::BirdPrelude.screen(candidate),cell:candidate,t:0.0}
  end
end
module TideboundBirdNewGame
  def start_new
    result=super
    $scene=Scene_TideboundBirdPrelude.new($scene)
    result
  end
end
Game.singleton_class.prepend(TideboundBirdNewGame)
