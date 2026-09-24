# New-game-only hide-and-seek. This never migrates an existing journey into it.
module Tidebound::PsychicMaze
  # GENERATED PUZZLE DATA
  MAP = 114
  START = [5,20].freeze
  PUSHERS = {[7,20]=>8,[3,9]=>8,[3,3]=>6,[9,3]=>2,[9,7]=>6,[17,7]=>2,[17,5]=>8}.freeze
  STOPS = [[7, 16], [17, 3], [17, 11]].freeze
  WARPS = {[9,16]=>[4,11],[4,10]=>[9,17],[7,11]=>[5,20],[16,3]=>[22,5],[22,6]=>[16,4]}.freeze
  # END GENERATED PUZZLE DATA
  module_function
  def active?; Tidebound::Opening.flags[:psychic_maze] == :active; end
  def arrival
    Tidebound::Opening.erase_autorun
    unless Tidebound::Opening.flags[:opening_started]
      Tidebound::Opening.begin_story
      return
    end
    Tidebound::Opening.travel(107,6,8,6) unless active?
  end
  def rules
    pbMessage("A scrap of paper: 'Arrows slide. Diamonds stop. Circles jump.'")
    pbMessage("Underneath, in your own writing: 'Find Wick!'")
  end
  def slide(direction)
    return unless active? && $game_map.map_id==MAP
    return if @moving
    @moving=true;original_speed=$game_player.move_speed;$game_player.move_speed=5
    seen={}
    160.times do
      point=[$game_player.x,$game_player.y];direction=PUSHERS[point] || direction
      key=point+[direction];break if seen[key];seen[key]=true
      dx,dy={2=>[0,1],4=>[-1,0],6=>[1,0],8=>[0,-1]}[direction]
      nx=point[0]+dx;ny=point[1]+dy;mask=Tidebound::MAP_PASSAGES[MAP]
      break unless nx>=0 && ny>=0 && mask[ny] && mask[ny][nx]=='1'
      break if $game_map.events.values.any? { |e| !e.through && e.x==nx && e.y==ny }
      command={2=>PBMoveRoute::DOWN,4=>PBMoveRoute::LEFT,6=>PBMoveRoute::RIGHT,8=>PBMoveRoute::UP}[direction]
      Tidebound::Opening.animate($game_player,[command])
      break if STOPS.include?([$game_player.x,$game_player.y]) || [$game_player.x,$game_player.y]==point
    end
  ensure
    $game_player.move_speed=original_speed if original_speed
    @moving=false
  end
  def warp(x,y)
    return unless active? && $game_map.map_id==MAP
    # Every landing is beside a pad, avoiding automatic return loops.
    pbFadeOutIn { $game_player.moveto(x,y);$game_player.turn_down;$game_map.refresh }
  end
  def finish
    return unless active? && $game_map.map_id==MAP
    pbMessage("Wick taps twice against the floor. You tap back. Found you.")
    pbMessage("Mother calls: Ren? Come downstairs, love. We need to talk.")
    flags=Tidebound::Opening.flags;flags[:psychic_maze]=:complete;flags[:bedroom_talk]=true
    Tidebound::Opening.travel(107,6,8,6)
    pbMessage("Your blanket is just where you left it.")
  end
end
