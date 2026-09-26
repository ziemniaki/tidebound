# Storehouse revision: preserve the original quest stages and trainer victories.
module Tidebound::Hideout
  module_function
  def q; Tidebound::NeighborQuest.q; end
  def say(*s); Tidebound::NeighborQuest.say(*s); end
  def active?; Tidebound::NeighborQuest.stage==:pursuit; end
  def actor; Tidebound::Opening.actor('Necklace thief'); end
  def sync
    return unless $game_map && $game_map.map_id==109
    e=actor;return unless e
    seated=!q[:second_won] && ![:necklace,:complete].include?(q[:stage])
    e.character_name=seated ? 'Tidebound_Ivo_Seated' : 'trainer_CAMPER'
    e.instance_variable_set(:@direction_fix,seated);e.instance_variable_set(:@step_anime,false)
    e.moveto(13,4) unless seated
    e.turn_down unless seated
  end
  def migrate
    return unless $game_map && $game_map.map_id==109
    return if q[:hideout_revision]==1
    # An old save may be beyond the new guard line or inside a rubbish pile.
    # Use the clear arrival once; preserve all quest, party and bag data.
    $game_player.moveto(11,14);q[:hideout_revision]=1
  end
  def arrival
    migrate;sync;Tidebound::Opening.erase_autorun
    return unless active? && !q[:heard]
    say('You step around a bowl with something growing in it.',
        'Bram: Boss said no more taking things from houses.',
        'Ivo: It was a SHOP. And stop talking. I am nearly through this bit.',
        'Packer: How much do pearls go for?', 'Bram: Depends on the pearl, probably.',
        'Packer: Shall I send them with the boxes?',
        'Bram: People at the docks buy anything from the coast. Let them work it out.',
        'Lookout: Our first proper Team Abyss job and nobody bought a broom.')
    q[:heard]=true
  end
  def clutter
    say('Empty bowls, stale crusts, damp socks and shipping wrappers.',
        'A note says: YOUR TURN TO TIDY. Three different names have been crossed out.')
  end
  def guard
    return say('Bram: He lost. Twice. I would leave him alone for a bit.') unless active? && !q[:runner_won]
    return unless Tidebound::NeighborQuest.able?
    say('Bram: Whoa. Quiet. He is playing.',
        'Bram: Last time somebody stood in front of the glass, he made us start from the beginning.',
        'Bram: You want to bother him? Get past me first.')
    return unless Tidebound::NeighborQuest.battle(:runner)==1
    q[:runner_won]=true
    say('Bram: All right. Your funeral. Just do not step on the handpiece.')
  end
  def approach
    return unless active? && !q[:runner_won]
    guard
    # Cancel/no able party must never let a player walk through the guard line.
    if $game_map.map_id==109 && !q[:runner_won]
      $game_player.moveto($game_player.x,10);$game_player.turn_up
    end
  end
  def play
    result=false
    pbFadeOutIn { result=Scene_TideboundMending.new.main }
    result
  ensure
    $game_map.autoplay if $game_map && $game_map.map_id==109
    Input.update
  end
  def console
    return boss if active?
    say('The little glass has gone dark. A thumbprint remains over the last rune.')
  end
  def cache
    return handoff if active? && q[:second_won]
    say('A cupboard of odd gloves, bent cutlery and things somebody meant to sell.')
  end
  def boss
    unless active?
      say('Ivo: I should not have taken it.', 'Ivo: I know. I am not asking you to say it is all right.');return
    end
    unless q[:runner_won]
      approach;return
    end
    unless q[:second_won]
      unless q[:hideout_game_won]
        say('Ivo does not look away from the little glass.',
            'Ivo: The necklace? Beat my game first. Then I might remember where I put it.')
        return unless pbConfirmMessage('Take the handpiece?')
        say('The wooden handpiece is warm. There are two worn thumb-stones.')
        unless play
          say('Ivo: Giving up? It is only a game.');return
        end
        q[:hideout_game_won]=true
        say('The room returns. A spoon falls from the sofa.',
            'Ivo: No. That does not count. You must have played it before.',
            'Ivo: Fine. A REAL battle. Then we will see.')
      else
        say('Ivo: Yes, yes. You beat the game. You still have to beat me.')
      end
      return unless Tidebound::NeighborQuest.able?
      e=actor
      if e
        e.character_name='trainer_CAMPER';e.instance_variable_set(:@direction_fix,false)
        e.turn_toward_player
      end
      result=Tidebound::NeighborQuest.battle(:second)
      unless result==1
        sync;return
      end
      q[:second_won]=true
      say('Ivo: ...I said I would tell you.',
          'Ivo: He is a decent old man. I knew that when I took it.',
          'Ivo: Come here. I put it away from this mess.')
      lead_to_cache
      follow_to_cache
    end
    handoff
  end
  def lead_to_cache
    e=actor;return unless e
    Tidebound::NeighborQuest.busy=true
    # The short route crosses a possible player interaction tile. Restore
    # collision afterward; never leave an invisible or through door blocker.
    through=e.through;e.through=true
    Tidebound::Opening.animate(e,[PBMoveRoute::DOWN,PBMoveRoute::LEFT,
      PBMoveRoute::LEFT,PBMoveRoute::LEFT,PBMoveRoute::UP,PBMoveRoute::TURN_LEFT])
  ensure
    if e
      e.moveto(13,4);e.through=through;e.instance_variable_set(:@direction_fix,false);e.turn_left
    end
    Tidebound::NeighborQuest.busy=false
  end
  def handoff
    return unless active? && q[:second_won]
    unless $bag.has?(Tidebound::NeighborQuest::NECKLACE) || $bag.add(Tidebound::NeighborQuest::NECKLACE,1)
      say('Ivo: Make room in your bag. I will keep it in this cupboard. No more games.');return
    end
    q[:stage]=:necklace;sync
    say('Ivo opens a small cloth bundle. The pearls are all there.',
        'Ivo: Here. Take it back to him. Tell him... No. I ought to tell him myself.',
        'You put the Pearl Necklace carefully in the Key Items pocket.')
  end
  def follow_to_cache
    return unless $game_map.map_id==109
    mask=Tidebound::MAP_PASSAGES[109]
    blocked=$game_map.events.values.reject(&:through).map { |e|[e.x,e.y] }
    start=[$game_player.x,$game_player.y];todo=[[start,[]]];seen={start=>true}
    directions=[[1,0,PBMoveRoute::RIGHT],[-1,0,PBMoveRoute::LEFT],
                [0,1,PBMoveRoute::DOWN],[0,-1,PBMoveRoute::UP]]
    until todo.empty?
      cell,route=todo.shift
      if cell==[13,5]
        Tidebound::Opening.animate($game_player,route+[PBMoveRoute::TURN_UP]);return
      end
      directions.each do |dx,dy,command|
        x=cell[0]+dx;y=cell[1]+dy;p=[x,y]
        next if x<0 || y<0 || !mask[y] || mask[y][x]!='1' || blocked.include?(p) || seen[p]
        seen[p]=true;todo<<[p,route+[command]]
      end
    end
  end
end

# Existing callers/tests/save events retain the old public entry points.
module TideboundHideoutQuest
  def runner; Tidebound::Hideout.guard; end
  def second_thief; Tidebound::Hideout.boss; end
  def overhear; Tidebound::Hideout.arrival; end
end
Tidebound::NeighborQuest.singleton_class.prepend(TideboundHideoutQuest)
EventHandlers.add(:on_new_spriteset_map,:tidebound_hideout,proc { |_s,_v|
  Tidebound::Hideout.migrate;Tidebound::Hideout.sync
})

# A fictional game inside the game. Its state never touches real Pokemon.
module Tidebound::Mending
  START=[9,10].freeze
  NESTS=[[3,2],[15,2],[9,4]].freeze
  EXIT=[9,0].freeze
  CELLS={}
  [[[9,0],[9,10]],[[3,8],[15,8]],[[3,4],[15,4]],[[3,2],[3,8]],[[15,2],[15,8]]].each do |a,b|
    x,y=a;dx=b[0]<=>x;dy=b[1]<=>y
    loop do
      CELLS[[x,y]]=true;break if [x,y]==b;x+=dx;y+=dy
    end
  end
  CELLS.freeze
  class Game
    attr_reader :cell,:freed,:bumps
    def initialize;@cell=START.dup;@freed=[];@bumps=0;end
    def move(dx,dy)
      p=[@cell[0]+dx,@cell[1]+dy]
      return false unless CELLS[p] && (p!=EXIT || @freed.length==3)
      @cell=p;true
    end
    def loosen
      i=NESTS.each_index.find { |n| !@freed.include?(n) && (NESTS[n][0]-@cell[0]).abs+(NESTS[n][1]-@cell[1]).abs<=1 }
      @freed<<i if i;i
    end
    def bump;@cell=START.dup;@bumps+=1;end
    def won?;@cell==EXIT && @freed.length==3;end
  end
end

class Scene_TideboundMending
  attr_reader :game
  def initialize
    @game=Tidebound::Mending::Game.new;@sprites=[];@bitmaps=[]
    @time=0.0;@next_move=0.0;@grace=0.0;@caption='Find three stitches. Let them sleep.'
  end
  def bitmap(w,h);b=Bitmap.new(w,h);@bitmaps<<b;b;end
  def sprite(b,z)
    s=Sprite.new(@viewport);s.bitmap=b;s.z=z;@sprites<<s;s
  end
  def ink(b,x,y,w,h,r,g,blue,a=255);b.fill_rect(x,y,w,h,Color.new(r,g,blue,a));end
  def oval(b,x,y,rx,ry,col)
    (-ry..ry).each do |dy|
      dx=(rx*Math.sqrt([1-(dy.to_f/ry)**2,0].max)).to_i
      b.fill_rect(x-dx,y+dy,dx*2+1,1,col)
    end
  end
  def line(b,x,y,xx,yy,col)
    steps=[(xx-x).abs,(yy-y).abs,1].max
    (0..steps).each { |n| b.fill_rect(x+(xx-x)*n/steps,y+(yy-y)*n/steps,1,1,col) }
  end
  def point(cell);[33+cell[0]*10,39+cell[1]*10];end
  def main
    build;@last=System.uptime
    pbBGMPlay('Tidebound Stillness',80,70)
    Graphics.transition(20)
    loop do
      Graphics.update;Input.update
      now=System.uptime;dt=[[now-@last,0.001].max,0.1].min;@last=now
      result=update(dt)
      return result unless result.nil?
    end
  ensure
    dispose
  end
  def dispose
    @sprites.reverse_each { |s|s.dispose unless s.disposed? }
    @bitmaps.reverse_each { |b|b.dispose unless b.disposed? }
    @viewport.dispose if @viewport && !@viewport.disposed?
  end
  def build
    @viewport=Viewport.new(0,0,Graphics.width,Graphics.height);@viewport.z=100000
    back=bitmap(256,192);ink(back,0,0,256,192,7,8,12)
    # A vast opened body: familiar Chansey outline, stretched egg-pouch/ribs,
    # bone seams and suspended Pokemon shapes. Pixel geometry, no stock gore.
    skin=Color.new(111,70,78);pale=Color.new(166,128,127);dark=Color.new(38,21,32)
    oval(back,128,89,106,78,dark);oval(back,128,89,96,73,skin)
    # Sagging, asymmetric skin lobes interrupt the recognisable egg silhouette.
    [[42,88,15,33],[207,102,17,28],[78,41,24,19],[172,52,31,19]].each do |x,y,rx,ry|
      oval(back,x,y,rx,ry,Color.new(122,77,82))
    end
    oval(back,128,101,78,56,Color.new(46,23,34))
    # Torn abdominal lips, pale connective tissue and exposed vertebrae.
    12.times do |i|
      y=53+i*9;spread=(Math.sqrt([1-((y-104)/58.0)**2,0].max)*76).to_i
      [-1,1].each do |side|
        x=128+side*spread
        oval(back,x,y,4,7,Color.new(171,102,104))
        line(back,x,y-3,x-side*6,y+5,Color.new(206,162,147))
        line(back,x+side*3,y,x+side*9,y+5,Color.new(69,26,42))
      end
    end
    9.times do |i|
      y=57+i*10;ink(back,119,y,7,4,155,128,117)
      ink(back,117,y+1,3,2,188,160,141);ink(back,126,y+2,3,2,83,48,60)
    end
    [-1,1].each do |side|
      5.times do |n|
        x=128+side*(86+n*2);y=45+n*12
        line(back,x,y,x+side*17,y-10,pale)
        line(back,x,y+2,x+side*13,y-3,skin)
      end
      7.times do |n|
        y=58+n*12
        3.times do |thick|
          line(back,128+side*72,y+thick,128+side*47,y+10+thick,pale)
          line(back,128+side*47,y+10+thick,128+side*22,y+12+thick,Color.new(126,95,97))
        end
        line(back,128+side*24,y+12,128+side*27,y+18,Color.new(176,98,109))
      end
      ey=side<0 ? 28 : 34
      oval(back,128+side*22,ey,8,4,Color.new(43,24,34))
      ink(back,122+side*22,ey,11,1,202,167,148)
      ink(back,128+side*22,ey,1,2,239,215,170)
      line(back,128+side*22,ey+4,125+side*22,ey+12,Color.new(65,32,47))
    end
    oval(back,123,44,12,8,Color.new(16,17,23))
    5.times { |i|ink(back,114+i*4,39,2,5,196,179,156) }
    # A long sutured facial tear: it cannot settle into a friendly smile.
    line(back,111,17,154,45,Color.new(41,25,37))
    6.times do |i|
      line(back,112+i*7,14+i*5,109+i*7,22+i*5,Color.new(196,174,149))
    end
    # Egg membrane, severed loops and dark drips remain in the non-walkable space.
    14.times do |n|
      x=42+(n*37)%174;y=54+(n*17)%106
      oval(back,x,y,4,7,Color.new(81,40,55));line(back,x,y,x-3,y+10,Color.new(144,66,76))
    end
    # Looped tissue at the cavity's lower edge; slow animation stays in the nests.
    5.times do |i|
      oval(back,78+i*22,152-(i%2)*4,13,6,Color.new(104,48,66))
      oval(back,78+i*22,152-(i%2)*4,9,3,Color.new(31,21,32))
      line(back,72+i*22,147-(i%2)*4,81+i*22,147-(i%2)*4,Color.new(165,94,105))
    end
    Tidebound::Mending::CELLS.each_key do |c|
      x,y=point(c);ink(back,x-4,y-4,9,9,32,38,41)
      ink(back,x-3,y+3,7,1,123,108,99)
    end
    @body=sprite(back,0);@body.zoom_x=@body.zoom_y=2
    live=bitmap(256,192);@live=sprite(live,2);@live.zoom_x=@live.zoom_y=2
    @icons=Bitmap.new('Graphics/Pokemon/Icons/NATU');@bitmaps<<@icons
    @text=bitmap(Graphics.width,Graphics.height);sprite(@text,5);pbSetSystemFont(@text)
    @veil=sprite(bitmap(Graphics.width,Graphics.height),6)
    @veil.bitmap.fill_rect(0,0,Graphics.width,Graphics.height,Color.new(6,9,14));@veil.opacity=255
    @title=bitmap(Graphics.width,Graphics.height);sprite(@title,7);pbSetSystemFont(@title)
    @title.font.color=Color.new(206,202,178);@title.font.size=26
    @title.draw_text(0,125,Graphics.width,40,'PET HOUSE',1)
    @title.font.size=20;@title.draw_text(0,175,Graphics.width,32,'Bring everyone home.',1)
    draw
  end
  def update(dt)
    @time+=dt
    if @time<3
      @veil.opacity=255;return nil
    end
    @title.clear unless @title_cleared
    @title_cleared=true;@veil.opacity=[255-((@time-3)*150).to_i,0].max
    return nil if @time<4.8
    return false if Input.trigger?(Input::BACK)
    if @finish_time
      @caption='They are light enough to carry now.'
      draw
      return true if @time-@finish_time>2.3
      return nil
    end
    if @time>=@next_move
      d={2=>[0,1],4=>[-1,0],6=>[1,0],8=>[0,-1]}[Input.dir4]
      if d && @game.move(*d);@next_move=@time+0.14;end
    end
    if Input.trigger?(Input::USE)
      i=@game.loosen
      unless i.nil?
        @caption=['Under the skin: a bird, still trying to sing.',
                  'The second mouth finally stops breathing.',
                  'It remembered RETURN. Nobody came.'][i]
        @caption_until=@time+4
      end
    end
    # Two slow contractions; several alternate routes and all freed nests persist.
    hazard=[9,6+(Math.sin(@time*0.75)>0 ? 0 : 1)]
    if @game.cell==hazard && @time>@grace
      @game.bump;@grace=@time+2
      @caption='The body swallows. The loose stitches stay loose.';@caption_until=@time+3
    end
    @caption=@game.freed.length==3 ? 'The mouth is open. Go north.' : 'Find three stitches. Let them sleep.' if @caption_until && @time>@caption_until
    @finish_time=@time if @game.won?
    draw
    nil
  end
  def draw
    b=@live.bitmap;b.clear
    pulse=(Math.sin(@time*1.5)*2).to_i
    Tidebound::Mending::NESTS.each_with_index do |c,i|
      x,y=point(c)
      if @game.freed.include?(i)
        oval(b,x,y,6,4,Color.new(15,21,26));ink(b,x-3,y,6,1,151,188,170)
        next
      end
      oval(b,x,y,11,12+pulse,Color.new(60,32,46))
      oval(b,x,y,8,10,Color.new(154,91,99))
      # Tiny native Natu silhouette embedded in an opened sac, held by sutures.
      b.stretch_blt(Rect.new(x-12,y-13,24,24),@icons,Rect.new(0,0,64,64))
      [-5,0,5].each do |off|
        line(b,x-8,y+off,x+8,y+off+2,Color.new(222,200,168))
        ink(b,x-8,y+off,2,3,49,27,37);ink(b,x+8,y+off+2,2,3,49,27,37)
      end
    end
    x,y=point([9,6+(Math.sin(@time*0.75)>0 ? 0 : 1)])
    oval(b,x,y,5,3+pulse.abs,Color.new(161,84,99))
    ink(b,x-4,y,8,1,233,181,162)
    x,y=point(@game.cell)
    oval(b,x,y+2,4,2,Color.new(8,15,21));ink(b,x-2,y-4,5,6,205,214,192)
    ink(b,x+1,y-3,1,2,35,41,43);ink(b,x-1,y+2,1,2,173,148,105)
    if @game.freed.length==3
      x,y=point(Tidebound::Mending::EXIT);ink(b,x-3,y-4,7,8,163,194,176)
    end
    @text.clear;@text.font.size=22;@text.font.color=Color.new(216,201,182)
    @text.fill_rect(0,0,Graphics.width,42,Color.new(7,8,12,245))
    @text.draw_text(12,4,Graphics.width-24,32,"THE MENDING     #{@game.freed.length} / 3",1)
    @text.fill_rect(0,320,Graphics.width,64,Color.new(7,8,12,245))
    @text.font.size=17;@text.draw_text(4,321,Graphics.width-8,30,@caption,1)
    @text.font.color=Color.new(158,172,165)
    @text.draw_text(4,352,Graphics.width-8,28,'Arrows: walk   Enter: loosen stitch   Esc: leave',1)
  end
end
