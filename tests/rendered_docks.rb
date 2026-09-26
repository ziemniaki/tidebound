# TEST ONLY: explicit door steps immediately after cutscenes, not direct transfers.
module DocksInput
  def trigger?(key)
    return Graphics.frame_count%4==0 if key==Input::USE
    super
  end
end
Input.singleton_class.prepend(DocksInput)
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('chosen-party.rxdata'))
  end
end
module DocksTest
  def shot(name)
    12.times { Graphics.update;updateSpritesets }
    b=Graphics.snap_to_bitmap;b.to_file("docks-#{name}.png");b.dispose
  end
  def step(dir)
    $game_player.public_send("move_#{dir}")
    25.times { Graphics.update;Input.update;update }
  end
  def update
    super
    return if @dock_test || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @dock_test=true;o=Tidebound::Opening;n=Tidebound::NeighborQuest;v=Tidebound::VaultVisit
    n.q[:stage]=:pursuit;n.q[:first_won]=true
    o.travel(108,35,42)
    e=o.actor('Running thief');e.moveto(35,42);e.through=true
    pbMoveRoute(e,[PBMoveRoute::UP])
    pbWait(0.025) while e.move_route_forcing
    e.opacity=0
    raise 'old bug not reproduced' if e.through || $game_player.passable?(35,42,8)
    File.write('DOOR_REPRO.txt','Native pbMoveRoute leaves hidden actor solid on entrance; player cannot step in.')
    e.moveto(31,43);e.through=true;n.witness_hideout
    raise 'hidden thief solid' unless e.through && e.opacity==0
    raise 'hideout not passable immediately' unless $game_player.passable?(35,42,8)
    step('up');raise 'hideout did not enter' unless $game_map.map_id==109
    n.q[:stage]=:complete;o.travel(106,8,8);o.oil_seller
    raise 'seller reward' unless v.q[:gift]
    e=o.actor('Seller outside')
    raise 'hidden seller solid' unless e.through && e.opacity==0
    # Stay on the same coast: no map reload allowed to mask the original bug.
    $game_player.moveto(*o.coast_xy(8,16))
    raise 'lighthouse not passable immediately' unless $game_player.passable?($game_player.x,$game_player.y,8)
    shot('lighthouse');step('up');raise 'lighthouse did not enter' unless $game_map.map_id==101
    # Camera-scroll alignment: inspect real atlas glass and compare pane coordinates.
    o.travel_coast(22,12);shot('shop-windows');step('right');shot('shop-scrolled')
    o.travel(108,35,42);shot('hideout-window')
    v.q[:open]=true;v.q[:talk]=true
    o.travel(112,14,28);shot('city-entrance')
    o.travel(112,32,23);shot('museum-pavement')
    o.travel(112,46,31);shot('warehouse-street')
    o.travel(112,26,47);shot('working-docks')
    o.travel(112,24,16);shot('residential-lane')
    raise 'night lost' unless $game_screen.tone.red==-80 && PBDayNight.isNight?
    lights=$scene.spriteset.usersprites.find { |x| x.is_a?(TideboundWindowLights) }
    raise 'window system missing' unless lights
    atlas=Bitmap.new('Graphics/Tilesets/'+$game_map.tileset_name)
    count=0
    lights.instance_variable_get(:@sprites).each do |sprite|
      x=sprite.instance_variable_get(:@tx);y=sprite.instance_variable_get(:@ty);id=$game_map.data[x,y,1]
      32.times do |py|;32.times do |px|
        c=sprite.bitmap.get_pixel(px,py);next if c.alpha==0
        source=atlas.get_pixel(((id-384)%8)*32+px,((id-384)/8)*32+py)
        raise 'light outside original glass' unless Tidebound::DockDetails.glass?(source,id)
        count+=1
      end;end
    end
    atlas.dispose;raise 'no lit pixels' if count==0
    # Old-save placement now covered by a new house relocates without resetting state.
    o.flags.delete(:dock_revision);$game_player.moveto(14,11);Tidebound::DockDetails.safe_dock_position
    raise 'save stranded in building' unless Tidebound::MAP_PASSAGES[112][$game_player.y][$game_player.x]=='1'
    raise 'gift lost' unless $bag.quantity(v::GIFT)==1
    File.write('DOCKS_PASS.txt',"PASS: reproduced old invisible collision; real immediate hideout/lighthouse entries; glass-only lighting #{count} pixels; viewport scroll; dock scenery/night; old-save safe placement.\n")
    exit
  rescue Exception=>e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('DOCKS_FAIL.txt',e.full_message);exit(1)
  end
end
Scene_Map.prepend(DocksTest)
