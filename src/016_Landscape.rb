# Additive landscape save migration; never resets quest, party or inventory data.
module Tidebound::Landscape
  REVISION = 2
  ANCHORS = {102=>[32,36],103=>[17,25],108=>[18,5],112=>[11,28],101=>[6,10],104=>[6,9],107=>[6,8],110=>[6,13],111=>[12,15]}.freeze
  module_function
  def safe_arrival
    map=$game_map
    return unless map && $game_player && ANCHORS.key?(map.map_id)
    revisions=(Tidebound::Opening.flags[:landscape_revisions] ||= {})
    return if revisions[map.map_id].to_i>=REVISION
    mask=Tidebound::MAP_PASSAGES[map.map_id]
    # Only the main connected walkable region is eligible, never an isolated ledge.
    start=ANCHORS[map.map_id];queue=[start];seen={start=>true};i=0
    while i<queue.length
      x,y=queue[i];i+=1
      [[x-1,y],[x+1,y],[x,y-1],[x,y+1]].each do |point|
        xx,yy=point
        next if xx<0 || yy<0 || !mask[yy] || mask[yy][xx]!='1' || seen[point]
        seen[point]=true;queue<<point
      end
    end
    occupied=map.events.values.reject(&:through).map { |e| [e.x,e.y] }
    triggers=map.events.values.select { |e| [1,2].include?(e.trigger) }.map { |e| [e.x,e.y] }
    old=[$game_player.x,$game_player.y]
    unless seen[old] && !occupied.include?(old)
      spot=queue.reject { |p| occupied.include?(p) || triggers.include?(p) }.min_by { |xx,yy| [(xx-old[0]).abs+(yy-old[1]).abs,yy,xx] }
      $game_player.moveto(*spot) if spot
    end
    moved=false
    $PokemonGlobal.followers.each do |data|
      next unless data.current_map_id==map.map_id && data.name=='Tidebound Pookie'
      next if seen[[data.x,data.y]]
      data.x,data.y=$game_player.x,$game_player.y;moved=true
    end
    $game_temp.followers=nil if moved
    revisions[map.map_id]=REVISION
  end
end
EventHandlers.add(:on_new_spriteset_map,:tidebound_landscape_arrival,proc { |_spriteset,_viewport|
  Tidebound::Landscape.safe_arrival
})
