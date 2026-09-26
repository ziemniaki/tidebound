# Disposable native integration/render fixture; never embedded in distribution.
module LandscapeInput
  def trigger?(key)
    return Graphics.frame_count%4==0 if key==Input::USE
    super
  end
end
Input.singleton_class.prepend(LandscapeInput)
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('chosen-party.rxdata'))
  end
end
module LandscapeCheck
  def shot(name)
    20.times { Graphics.update;Input.update;updateSpritesets }
    bitmap=Graphics.snap_to_bitmap;bitmap.to_file("landscape-#{name}.png");bitmap.dispose
  end
  def step(dir)
    $game_player.public_send("move_#{dir}")
    25.times { Graphics.update;Input.update;update }
  end
  def update
    super
    return if @landscape_check || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @landscape_check=true
    o=Tidebound::Opening;n=Tidebound::NeighborQuest;v=Tidebound::VaultVisit
    ids=$player.party.map(&:personalID);candies=$bag.quantity(:RARECANDY)
    o.travel_coast(8,16);shot('garden')
    raise 'lighthouse blocked' unless $game_player.passable?($game_player.x,$game_player.y,8)
    step('up');raise 'lighthouse entry' unless $game_map.map_id==101
    o.travel_coast(53,20);shot('pier')
    o.travel(103,17,12);shot('wood-keys')
    o.travel(103,25,11);shot('wood-pool')
    o.travel(103,11,22);shot('wood-camp')
    o.travel(108,26,19);shot('road-crossing')
    n.q[:stage]=:pursuit;n.q[:first_won]=true;n.q[:hideout_seen]=true;n.q[:heard]=true
    o.travel(108,35,42)
    e=o.actor('Running thief');e.opacity=0;e.through=true
    shot('road-hideout')
    raise 'hideout blocked' unless $game_player.passable?(35,42,8)
    step('up');raise 'hideout entry' unless $game_map.map_id==109
    v.q[:open]=true;v.q[:talk]=true
    o.travel(112,32,14);shot('dock-garden')
    o.travel(112,26,47);shot('docks')
    [102,103,108,112].each do |mid|
      anchor=Tidebound::Landscape::ANCHORS[mid];o.travel(mid,*anchor)
      raise 'tileset did not load' unless $game_map.tileset_name=='TideboundLandscape'
      mask=Tidebound::MAP_PASSAGES[mid]
      # A saved position inside a newly solid tree/rock is moved into the reachable area.
      blocked=nil
      mask.each_with_index do |row,y|
        row.each_char.with_index do |cell,x|
          if cell=='0' && x>3 && y>3 && $game_map.data[x,y,2]>0
            blocked=[x,y];break
          end
        end
        break if blocked
      end
      raise 'no landscape solids' unless blocked
      o.flags[:landscape_revisions].delete(mid)
      $game_player.moveto(*blocked);Tidebound::Landscape.safe_arrival
      raise 'old-save position stranded' unless mask[$game_player.y][$game_player.x]=='1'
      position=[$game_player.x,$game_player.y];Tidebound::Landscape.safe_arrival
      raise 'migration not idempotent' unless position==[$game_player.x,$game_player.y]
      raise 'night lost' unless $game_screen.tone.red==-80 && PBDayNight.isNight?
    end
    raise 'party changed' unless $player.party.map(&:personalID)==ids
    raise 'inventory changed' unless $bag.quantity(:RARECANDY)==candies
    o.travel_coast(22,12);shot('shop-window')
    lights=$scene.spriteset.usersprites.find { |s| s.is_a?(TideboundWindowLights) }
    raise 'windows absent' unless lights
    count=lights.instance_variable_get(:@sprites).sum { |s| s.pane_pixels.length }
    raise 'no window glass' unless count>0
    [103,108].each do |mid|
      o.travel(mid,*Tidebound::Landscape::ANCHORS[mid]);grass=0
      $game_map.height.times do |y|;$game_map.width.times do |x|
        if $game_map.data[x,y,1]==391 && Tidebound::MAP_PASSAGES[mid][y][x]=='1'
          raise 'grass lost terrain' unless $game_map.terrain_tag(x,y).land_wild_encounters
          grass+=1
        end
      end;end
      raise 'too little accessible grass' unless grass>=8
    end
    # Audit every transition cue and save a view of every doorway on all 13 maps.
    anchors={101=>[6,10],102=>[32,36],103=>[17,25],104=>[6,9],105=>[15,21],106=>[8,10],107=>[6,8],108=>[18,5],109=>[11,14],110=>[6,13],111=>[12,15],112=>[11,28],113=>[14,18]}
    cue_count=0
    anchors.each do |mid,anchor|
      o.travel(mid,*anchor)
      cues=$scene.spriteset.usersprites.select { |s| s.is_a?(TideboundThreshold) }
      expected=$game_map.events.values.count { |e| Tidebound::FieldDetails::EXITS.include?(e.name) }
      raise 'missing doorway cue' unless cues.length==expected
      cues.each_with_index do |cue,i|
        x,y=cue.tile_anchor
        # Camera preview may centre on a solid stair; real navigation was checked separately.
        $game_player.moveto(x,[y+1,$game_map.height-1].min)
        shot("door-#{mid}-#{i}")
        rx=(x*Game_Map::REAL_RES_X-$game_map.display_x)/Game_Map::X_SUBPIXELS
        ry=(y*Game_Map::REAL_RES_Y-$game_map.display_y)/Game_Map::Y_SUBPIXELS
        raise 'cue does not follow tile/camera' unless cue.x==rx && cue.y==ry
        raise 'lighthouse sill offset' if mid==102 && x==32 && y==35 && cue.cue_rect!=[5,1,22,3]
        raise 'west exit orientation' if mid==112 && x==10 && y==28 && cue.cue_rect!=[1,5,3,22]
        cue_count+=1
      end
    end
    File.write('DOOR_AUDIT.txt',"#{cue_count} transition cues audited across 13 maps; tile/camera anchor and lighthouse sill verified.")
    saved=Marshal.load(Marshal.dump(SaveData.compile_save_hash))
    SaveData.mark_values_as_unloaded;SaveData.load_all_values(saved)
    raise 'save round trip lost progress' unless o.flags[:landscape_revisions].values.all? { |r| r==2 } && $player.party.map(&:personalID)==ids && $bag.quantity(:RARECANDY)==candies
    File.write('LANDSCAPE_PASS.txt',"PASS: 4 native outdoor maps, 10 rendered views, real lighthouse/hideout door steps, perpetual night, window panes, grass terrain, additive blocked-position recovery and idempotence, preserved party/inventory.\n")
    exit
  rescue Exception=>e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('LANDSCAPE_FAIL.txt',e.full_message);exit(1)
  end
end
Scene_Map.prepend(LandscapeCheck)
