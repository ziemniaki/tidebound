# Native Pokemon/bag/save objects, staged battle outcomes; no graphics claims.
module Tidebound::Hideout
  class << self
    alias real_play play
    def play;$hideout_plays=($hideout_plays||0)+1;$hideout_result;end
  end
end
class OpeningEvent
  attr_accessor :character_name
  def turn_toward_player;end
end
def hideout_setup
  new_opening
  $player.party=[Pokemon.new(:NATU,7,$player)]
  Tidebound::NeighborQuest.q.merge!(stage: :pursuit,first_won: true,heard: true)
  Tidebound::Opening.travel(109,11,14)
  $game_map.events={1=>OpeningEvent.new('Necklace thief',1,16,4)}
  $quest_outcome=1;$hideout_plays=0;$hideout_result=true
end
h=Tidebound::Hideout;n=Tidebound::NeighborQuest;o=Tidebound::Opening
hideout_setup
h.migrate;check([$game_player.x,$game_player.y]==[11,14],'migration entry')
$game_player.moveto(4,10);h.migrate;check($game_player.x==4,'repeated migration')
$quest_outcome=0;$game_player.moveto(14,9);h.approach
check(!n.q[:runner_won] && $game_player.y==10 && $hideout_plays==0,'guard skipped on abort')
$quest_outcome=1;h.approach;check(n.q[:runner_won],'guard win')
$hideout_result=false;h.boss
check(!n.q[:hideout_game_won] && !n.q[:second_won] && n.stage==:pursuit,'cancel advances')
$hideout_result=true;$quest_outcome=2;h.boss
check(n.q[:hideout_game_won] && !n.q[:second_won] && Tidebound.state.realm==:astral,'boss loss')
check(Tidebound.state.souls.last.pokemon.hp==0,'boss loss snapshot')
roundtrip
point=Tidebound.return_to_living!;o.travel(*point);o.travel(109,11,14)
$quest_outcome=1;calls=$hideout_plays;$quest_reject_item=n::NECKLACE;h.boss
check(n.q[:second_won] && n.stage==:pursuit && calls==$hideout_plays,'win/full bag/replay')
roundtrip;$quest_reject_item=nil;h.cache
check(n.stage==:necklace && $bag.quantity(n::NECKLACE)==1,'cache collection')
h.boss;h.cache;check($bag.quantity(n::NECKLACE)==1,'duplicate necklace')
o.travel(106,8,10);n.return_necklace
check(n.stage==:complete && !$bag.has?(n::NECKLACE),'seller continuation')
hideout_setup;n.q[:runner_won]=true;n.q[:second_won]=true
h.boss;check(n.stage==:necklace && $hideout_plays==0,'legacy defeated boss replays')
puts 'PASS: guard/abort; minigame cancel/win; astral boss loss; saved win skips replay; full-bag/cache retry; unique necklace; seller return; legacy defeated boss.'

g=Tidebound::Mending::Game.new
def mending_walk(g,goal)
  todo=[[g.cell,[]]];seen={g.cell=>true};route=nil
  until todo.empty?
    cell,path=todo.shift
    if cell==goal;route=path;break;end
    [[1,0],[-1,0],[0,1],[0,-1]].each do |dx,dy|
      p=[cell[0]+dx,cell[1]+dy]
      next unless Tidebound::Mending::CELLS[p] && !seen[p]
      seen[p]=true;todo<<[p,path+[[dx,dy]]]
    end
  end
  raise 'unreachable nest' unless route
  route.each { |dx,dy|check(g.move(dx,dy),'route rejected') }
end
g.move(1,0);check(g.cell==[9,10],'wall crossing')
mending_walk(g,[9,1]);check(!g.move(0,-1),'exit opens early')
Tidebound::Mending::NESTS.each_with_index do |cell,i|
  mending_walk(g,cell);check(g.loosen==i,'nest not released')
  check(g.loosen.nil?,'duplicate nest');g.bump;check(g.freed.length==i+1,'bump reset progress')
end
mending_walk(g,Tidebound::Mending::EXIT);check(g.won?,'exit not won')
puts 'PASS: minigame walls, all reachable nests, three-release exit gate, contraction preserves progress.'
