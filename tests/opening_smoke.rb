# Integration smoke: actual Essentials data, player, Pokemon and interpreter;
# graphics, messages and scene transfers are replaced by deterministic fixtures.
module EventHandlers
  @handlers = {}
  def self.add(event,key,callback); (@handlers[event] ||= {})[key]=callback; end
  def self.trigger(event,*args); (@handlers[event]||{}).each_value { |p| p.call(*args) }; end
end
class Game_Map
  attr_accessor :events, :map_id
  def refresh; end
end
class OpeningEvent
  attr_reader :erased
  def erase; @erased=true; end
end
class OpeningPlayerLocation
  attr_accessor :x,:y
  def initialize; @x=6;@y=10; end
  def moveto(x,y);@x=x;@y=y;end
  def turn_up;end
  def turn_down;end
  def refresh_charset;end
  def move_route_forcing; false; end
end
class Game_Temp
  attr_accessor :player_new_map_id,:player_new_x,:player_new_y,:player_new_direction
end
class OpeningScene
  def transfer_player
    $game_map.map_id=$game_temp.player_new_map_id
    $game_player.moveto($game_temp.player_new_x,$game_temp.player_new_y)
  end
end
class OpeningGlobal
  attr_accessor :pokecenterMapId
end
$messages=[];$choices=[]
def pbMessage(text,choices=nil,*args)
  $messages << text
  choices ? ($choices.shift || 0) : nil
end
def pbConfirmMessage(text);pbMessage(text);($choices.shift != false);end
def pbConfirmMessageSerious(text);pbConfirmMessage(text);end
def pbFadeOutIn(*args);yield;end
def pbMapInterpreter; $opening_interpreter;end
class OpeningEvent
  attr_accessor :name, :id, :x, :y, :opacity, :through, :step_anime
  def initialize(name="Opening", id=1, x=11, y=16)
    @name=name; @id=id; @x=x; @y=y
  end
  def moveto(x,y); @x=x; @y=y; end
  def move_route_forcing; false; end
end
module PBMoveRoute
  DOWN=1; LEFT=2; RIGHT=3; UP=4; JUMP=14
  TURN_RIGHT=18; TURN_DOWN=16; CHANGE_SPEED=29
end
def pbMoveRoute(*args); end
class Pokemon
  def self.play_cry(*args); end
end
module Followers
  def self.add(id,name,_common); @dog=$game_map.events[id]; end
  def self.get(_name); @dog; end
  def self.remove(_name); @dog=nil; end
end
module System
  def self.uptime; 0; end
end

def pbWait(seconds);yield seconds if block_given?;end

class OpeningPlayerLocation
  attr_accessor :direction,:through
  def direction; @direction || 2; end
  def turn_left; @direction=4; end
  def turn_right; @direction=6; end
end
class OpeningEvent
  attr_accessor :direction
  def turn_up; @direction=8; end
  def turn_down; @direction=2; end
  def turn_left; @direction=4; end
  def turn_right; @direction=6; end
end
module PBMoveRoute
  TURN_UP=19; TURN_LEFT=17
end
