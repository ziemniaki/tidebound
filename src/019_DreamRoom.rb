# Two false bedrooms. Dream time and fragmented writing are not reliable history.
module Tidebound::DreamRoom
  MAP=115
  FOLDED_MAP=116
  START=[7,8].freeze
  FOLDED_START=[7,22].freeze
  QUESTIONS=[
    ["What colour is a door that has never been opened?",["Blue","Thursday","The colour of wood"],1],
    ["Who was here before you arrived?",["Someone","Nobody","The empty chair"],2],
    ["Where does the sea sleep when it forgets the shore?",["Under the pillow","Inside the clock","Nowhere"],0]
  ].freeze
  FOLDED_QUESTIONS=[
    ["Which tooth keeps the house standing?",["A loose tooth","Beneath the floor","Noon's tooth"],1],
    ["What remains when the widow subtracts her name?",["A mouthful of snow","Nine empty sleeves","The name of the knife"],0],
    ["How many times must an empty cradle be buried?",["Until it stops","Once for each sleeper","Before"],2],
    ["Who knocks from inside the last page?",["Child-shaped rain","Nobody in your voice","The outside hand"],1]
  ].freeze
  DURATIONS=['5 seconds','5 minutes','5 hours','5 days','5 months','5 years','12 years'].freeze
  TEXT={
    chair:["The empty chair was here before you.","It has been practising your weight."],
    shelf:["The books are arranged by the sound they make when nobody reads them.","Every last page says: CONTINUED BEFORE."],
    window:["There is a room outside the window.","Its window is looking in."],
    clock:["Tick. Tock. Tick. Thursday.","One hand points to the hour. The other points at you."],
    book:["A small book of useful colours. Blue. Red. Thursday.","Beside THURSDAY: a door with no handle. The page is warm."],
    lamp:["The lamp is full of yesterday's light.","Something inside it is trying to remember a moth."],
    plant:["The leaves turn towards a sun that has not been born.","At the bottom of the pot: hush hush hush."],
    rug:["Someone has woven a way home into the rug.","You cannot find the first thread."]
  }.freeze
  FOLDED_TEXT={
    tooth:["A primer of houses. A primer of teeth. The same drawing.","THE ONE BENEATH THE FLOOR KEEPS THE HOUSE STANDING.","Do not count the windows with your tongue."],
    snow:["A widow writes her name. Scratches it out. Writes it smaller.","NAME LESS NAME: A MOUTHFUL OF SNOW.","The snow has learned to shut a door."],
    cradle:["A burial register. Every entry is an empty cradle.","How many times? The column says BEFORE. Before. Before.","There are no numbers left in this house."],
    voice:["The last page has knuckles. You turn it; they turn with it.","NOBODY, WEARING YOUR VOICE. That is who knocks.","The next page is the back of your throat."],
    empty_bed:["This bed has been slept beside.","The hollow in the blanket is facing the wrong way."],
    chair:["A chair for the part of you that stayed downstairs.","There is no downstairs."],
    plant:["The roots are tied in the shape of a small apology.","It was not accepted."],
    cupboard:["Four little books. Their covers are made of yesterday.","Tooth. Snow. Cradle. Voice. The shelves have put them elsewhere."]
  }.freeze
  class << self;attr_accessor :wick_alpha;end
  module_function
  def q;Tidebound::Opening.flags[:dream_room] || {};end
  def active?;[:sealed,:wick,:folded].include?(q[:phase]);end
  def wick_visible?;q[:phase]==:wick;end
  def say(*lines);lines.each { |s|pbMessage(s) };end
  def arrival
    Tidebound::Opening.erase_autorun
    unless Tidebound::Opening.flags[:opening_started]
      Tidebound::Opening.begin_story
      return
    end
    if q[:phase]==:folded
      Tidebound::Opening.travel(FOLDED_MAP,*FOLDED_START,8)
    elsif !active?
      return_to_journey
    end
  end
  def return_to_journey
    if Tidebound::PsychicMaze.active?
      Tidebound::Opening.travel(114,5,20,2)
    else
      Tidebound::Opening.travel(107,6,8,6)
    end
  end
  def inspect_object(kind)
    return unless active?
    say(*TEXT.fetch(kind))
    return unless kind==:shelf
    choice=pbMessage("One book sits with its spine against the wall.",['Leave it','Turn the book'],-1)
    return unless choice==1
    choice=pbMessage("A loose leaf is stitched into the back board.",['Water curse','Put it back'],-1)
    water_curse if choice==0
  end
  def cupboard
    return unless active?
    say("Three small books. None has a first page.")
    loop do
      choice=pbMessage("The cupboard smells of rain.",['On unopened doors','The previous occupant','Where the sea sleeps','Close the cupboard'],-1)
      case choice
      when 0
        say("THURSDAY IS NOT A DAY.","IT IS THE COLOUR OF A DOOR THAT HAS NEVER BEEN OPENED.","A worm has eaten the middle of every O.")
      when 1
        say("BEFORE YOU: THE EMPTY CHAIR.","AFTER YOU: LEAVE A LITTLE SPACE.")
      when 2
        say("THE SEA SLEEPS UNDER THE PILLOW.","DO NOT TURN IT OVER.","A pressed flower falls out. Its shadow is twelve years long.")
      else
        say("The books close a moment before your hand reaches them.")
        break
      end
    end
  end
  # Compatibility for cached 0.7.18 event commands; no computer is displayed.
  def computer;cupboard;end

  # A quiet, visible fold: runes gather, the body fades/turns, then unwinds at home.
  # No full-screen flash or shake. Always restore runtime state, even on exceptions.
  def fold_to(x,y)
    player=$game_player;old_opacity=player.opacity;old_direction=player.direction
    viewport=Viewport.new(0,0,Graphics.width,Graphics.height);viewport.z=99997
    bitmap=Bitmap.new(128,128)
    ink=Color.new(162,181,199,165)
    40.times do |i|
      a=i*Math::PI/20;xx=64+(Math.cos(a)*43).round;yy=64+(Math.sin(a)*30).round
      bitmap.fill_rect(xx,yy,3,3,ink)
    end
    [[32,44],[82,41],[54,85],[92,70]].each do |xx,yy|
      bitmap.fill_rect(xx,yy,2,10,ink);bitmap.fill_rect(xx,yy,8,2,ink);bitmap.fill_rect(xx+6,yy+6,2,6,ink)
    end
    sprite=Sprite.new(viewport);sprite.bitmap=bitmap;sprite.ox=64;sprite.oy=64
    2.times do |half|
      20.times do |i|
        progress=(i+1)/20.0
        player.opacity=(old_opacity*(half==0 ? 1-progress : progress)).to_i
        player.direction=[2,4,8,6][(i/5)%4]
        sprite.x=player.screen_x;sprite.y=player.screen_y-16
        sprite.angle=(half==0 ? i*4 : 80-i*4)
        sprite.zoom_x=sprite.zoom_y=(half==0 ? 1.25-progress*0.8 : 0.45+progress*0.8)
        sprite.opacity=(Math.sin(progress*Math::PI)*190).to_i
        pbWait(0.025)
      end
      player.moveto(x,y) if half==0
    end
  ensure
    player.opacity=old_opacity if player && old_opacity
    player.direction=old_direction if player && old_direction
    sprite&.dispose;bitmap&.dispose;viewport&.dispose
  end
  def exit_loop
    return unless active? && $game_map.map_id==MAP
    count=q[:door_loops].to_i;q[:door_loops]=count+1
    fold_to(*START)
    say(["You are already here.","The stairs remember going down. You don't.","A small room. A smaller return."][count%3])
  end
  def on_bed(x,y,return_x,return_y)
    map=$game_map.map_id
    pbFadeOutIn { $game_player.moveto(x,y);$game_player.turn_up }
    yield
  ensure
    if $game_map.map_id==map
      pbFadeOutIn { $game_player.moveto(return_x,return_y);$game_player.turn_down }
    end
  end
  def bed
    return unless active? && $game_map.map_id==MAP
    if wick_visible?
      say("The pillow is warm on both sides. Something small is waiting for you.")
      return
    end
    on_bed(3,5,4,7) do
      say("The pillow has kept a place for your head.","Under the ticking, a voice asks three things.") unless q[:riddles_solved]
      unless q[:riddles_solved]
        q[:streak]=0
        QUESTIONS.each do |question,answers,right|
          answer=pbMessage(question,answers,-1)
          if answer!=right
            q[:streak]=0
            say(answer<0 ? "You lift your head. The questions fold themselves away." : "The pillow has forgotten your first answer. Begin again.")
            return
          end
          q[:streak]+=1
        end
        q[:riddles_solved]=true
        say("Three answers. A little room opens inside the silence.")
      end
      choice=pbMessage("How long would you like to sleep?",DURATIONS+['Stay awake'],-1)
      sleep_for(choice) if choice.between?(0,6)
    end
  end
  def sleep_for(choice)
    return unless active? && q[:riddles_solved] && choice.between?(0,6)
    q[:last_sleep]=DURATIONS[choice]
    pbFadeOutIn do
      pbWait(0.45)
      if choice==6
        q[:phase]=:wick;self.wick_alpha=0
      end
    end
    if choice==6
      say("You wake to the sound of two small taps.")
      24.times { |i|self.wick_alpha=((i+1)*255/24);pbWait(0.03) }
    else
      say(["Five seconds. The clock disagrees.","A minute is missing from the others.","The same light is waiting for you.","There is no dust on tomorrow.","The leaves have not learned another season.","You wake with a word on your tongue. It isn't yours."][choice])
    end
  ensure
    self.wick_alpha=nil
  end
  def wick
    return unless wick_visible? && $game_map.map_id==MAP
    say("Wick opens his beak. The sound comes from behind you.")
    q[:phase]=:folded;q[:folded_streak]=0
    Tidebound::Opening.travel(FOLDED_MAP,*FOLDED_START,8)
  end
  def folded_arrival
    Tidebound::Opening.erase_autorun
    unless q[:phase]==:folded
      return_to_journey
      return
    end
    return if q[:folded_seen]
    q[:folded_seen]=true
    say("Your room. There is more of it than there was.","Somewhere, a pillow is holding its breath.")
  end
  def folded_reading(kind)
    return unless q[:phase]==:folded
    say(*FOLDED_TEXT.fetch(kind))
  end
  def folded_reset
    return unless q[:phase]==:folded && $game_map.map_id==FOLDED_MAP
    q[:folded_streak]=0;q[:folded_resets]=q[:folded_resets].to_i+1
    fold_to(*FOLDED_START)
    say("The room puts you back at the beginning. It keeps the part that answered.")
  end
  def folded_bed
    return unless q[:phase]==:folded && $game_map.map_id==FOLDED_MAP
    wrong=false
    on_bed(24,5,25,7) do
      say("Four questions have been sleeping in your place.")
      q[:folded_streak]=0
      FOLDED_QUESTIONS.each do |question,answers,right|
        answer=pbMessage(question,answers,-1)
        if answer!=right
          wrong=true;break
        end
        q[:folded_streak]+=1
      end
      unless wrong
        q[:phase]=:complete
        Tidebound::Opening.flags[:psychic_maze]=:active
        say("The bed remembers being a bed.","Two small taps. This time, from somewhere you can reach.")
        Tidebound::Opening.travel(114,5,20,2)
        say("Somewhere beyond the shelves, Wick taps back. One more game.")
      end
    end
    folded_reset if wrong
  end

  CURSE_PAGES=[
    ["W A T E R   C U R S E", "a leaf without a tree / a room without outside",
     "give the water a word give the word a hollow",
     "do not give it the hollow where the word was",
     "under under under the hem of the shore",
     "the cup is carrying the mouth carrying the cup",
     "you said you said you said you were asleep",
     "the ink has knees / it kneels the wrong way",
     "salt remembers a shape that has not happened",
     "turn the page before it learns your fingers",
     "///////////// hush hush hush //////////////"],
    ["a bed a bed a b e d a b e d a b", "there is no water here there is no here",
     "the tide has written itself on the back of the tide",
     "seven little doors inside a single closed eye",
     "open the seventh / there were never seven",
     "a lullaby with all the mouths rubbed out",
     "WHERE IS THE SHORE WHEN THE SHORE IS WORN",
     "worn warm worm word ward water w a t e r",
     "the margin cannot hold the margin cannot hold",
     "the margin cannot hold the margin cannot hold",
     "a name turned face-down / it is still listening"],
    ["do not read the wet part", "do not wet the read part / part the not / read",
     "a small bell full of hair rings without a bell",
     "the sleeve reaches out for what should be an arm",
     "give back the bottom of the bowl",
     "give back the inside of the knock",
     "give back the give back the give back the",
     "the house has swallowed its nearest house",
     "THIS IS NOT THE FIRST SIDE OF THE PAPER",
     "this is not the first side this is not the first",
     "//// before before before before before ////"],
    ["the writing thins / something keeps writing",
     "water curse water course water cradle water",
     "if you find an ending leave it where it lies",
     "a clean dry leaf / a clean dry leaf / a clean",
     "there is nothing under your thumb but tomorrow",
     "tomorrow has no underside no underside no",
     "hush little room / let the room go home",
     "a word is missing from every missing word",
     "................................................",
     "the page is dry",
     "your hand is dry / your hand is dry / your hand"]
  ].freeze
  def water_curse
    return unless active?
    q[:water_curse_read]=true
    viewport=Viewport.new(0,0,Graphics.width,Graphics.height);viewport.z=100000
    shade=Sprite.new(viewport);shade.bitmap=Bitmap.new(Graphics.width,Graphics.height)
    shade.bitmap.fill_rect(0,0,Graphics.width,Graphics.height,Color.new(10,14,25,240))
    sheet=Sprite.new(viewport);sheet.bitmap=Bitmap.new(Graphics.width+120,Graphics.height)
    strip=Sprite.new(viewport);strip.bitmap=Bitmap.new(Graphics.width+120,20)
    footer=Sprite.new(viewport);footer.bitmap=Bitmap.new(Graphics.width,40);footer.y=Graphics.height-40
    pbSetSystemFont(sheet.bitmap);pbSetSystemFont(footer.bitmap)
    sheet.bitmap.font.size=22;footer.bitmap.font.size=18
    CURSE_PAGES.each_with_index do |lines,page|
      sheet.bitmap.clear;footer.bitmap.clear
      lines.each_with_index do |line,i|
        sheet.bitmap.font.color=Color.new(i%3==0 ? 168 : 195,180,i%3==0 ? 195 : 175)
        sheet.bitmap.draw_text(10+(i%3)*13,5+i*28,Graphics.width+105,32,line)
      end
      footer.bitmap.font.color=Color.new(163,179,188)
      footer.bitmap.draw_text(16,4,Graphics.width-32,30,"#{page+1}/4    Confirm: turn page    Cancel: close")
      strip.bitmap.clear;strip.bitmap.blt(0,0,sheet.bitmap,Rect.new(0,80+page*28,Graphics.width+120,18))
      elapsed=0
      loop do
        Graphics.update;Input.update;elapsed+=1
        sheet.x=elapsed%90<8 ? -3 : 0
        strip.y=80+page*28;strip.x=((elapsed/12)%3-1)*7
        strip.opacity=60+(elapsed/20%3)*20
        next if elapsed<16
        break if Input.trigger?(Input::USE)
        return if Input.trigger?(Input::BACK)
      end
    end
  ensure
    [footer,strip,sheet,shade].each { |s|s&.bitmap&.dispose;s&.dispose }
    viewport&.dispose
    Input.update
  end
end
# Refresh only the edited dream map in old saves; never reset unrelated map events.
module TideboundDreamMapRefresh
  def load_map
    $map_factory.setup(115) if $map_factory && $map_factory.map.map_id==115
    super
  end
end
Game.singleton_class.prepend(TideboundDreamMapRefresh)
