# New-game-only hide-and-seek. This never migrates an existing journey into it.
module Tidebound::PsychicMaze
  module_function
  def active?; Tidebound.story[:psychic_maze] == :active; end
  def arrival
    Tidebound::World.erase_autorun
    unless Tidebound.story[:opening_started]
      Tidebound::Opening.begin_story
      return
    end
    Tidebound::World.travel(:bedroom,6,8,6) unless active?
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
      Tidebound::World.animate($game_player,[command])
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
    flags=Tidebound.story;flags[:psychic_maze]=:complete;flags[:bedroom_talk]=true
    Tidebound::World.travel(:bedroom,6,8,6)
    pbMessage("Your blanket is just where you left it.")
  end
end
