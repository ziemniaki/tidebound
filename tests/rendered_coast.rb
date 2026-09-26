# TEST ONLY. Disposable game copy, no player saves. Native engine with automated input.
$stdout.sync=true
puts 'COAST: loaded test'
module TideboundCoastInput
  def trigger?(key)
    if Graphics.frame_count % 600 == 0
      puts "COAST frame #{Graphics.frame_count}: #{$scene.class}"
      b=Graphics.snap_to_bitmap;b.to_file('debug-coast.png');b.dispose
    end
    return Graphics.frame_count % 6==0 if key==Input::USE
    super
  end
end
Input.singleton_class.prepend(TideboundCoastInput)
EventHandlers.add(:on_frame_update,:coast_capture_lapras,proc {
  if Tidebound::SeaGlimpse.visible && Tidebound::SeaGlimpse.alpha.to_i>=135 && !$tb_lapras_shot
    b=Graphics.snap_to_bitmap;b.to_file('lapras.png');b.dispose;$tb_lapras_shot=true
  end
})
module TideboundCoastCheck
  def shot(name)
    5.times { Graphics.update; updateSpritesets }
    b=Graphics.snap_to_bitmap;b.to_file("#{name}.png");b.dispose
    puts "COAST: #{name}"
  end
  def coast_step(direction)
    old=[$game_player.x,$game_player.y]
    $game_player.public_send("move_#{direction}")
    25.times { Graphics.update; Input.update; update }
    raise "blocked step #{direction} #{old}" if old==[$game_player.x,$game_player.y]
  end
  def update
    super
    return if @coast_check || !$player || !$game_map || $game_map.map_id!=107
    o=Tidebound::Opening
    return unless Tidebound.story[:opening_started]
    return if pbMapInterpreterRunning? || $game_temp.message_window_showing
    @coast_check=true
    puts 'COAST: start'
    # The unchanged bedroom and hall were rendered in 0.4. Focus on changed coast.
    Tidebound.story.merge!({:bedroom_talk=>true,:hall_talk=>true,:walk_state=>:requested})
    Tidebound::World.travel_coast(5,11);shot('lighthouse')
    Tidebound::World.travel_coast(15,19);shot('causeway')
    Tidebound::World.travel_coast(28,22);shot('beach')
    Tidebound::World.travel_coast(10,16);o.pookie
    Tidebound.story[:walk_steps]=98
    coast_step('down');coast_step('left')
    raise 'walk distance' unless Tidebound.story[:walk_steps]==100 && Followers.get(o::POOKIE_FOLLOWER)
    raise 'save follower' unless Game.save('coast-following.rxdata')
    data=SaveData.get_data_from_file('coast-following.rxdata')
    data[:tidebound].story.delete(:coast_revision)
    data[:game_system].magic_number=26090904
    gp=data[:game_player]
    gp.instance_variable_set(:@x,gp.x-24);gp.instance_variable_set(:@y,gp.y-20)
    gp.instance_variable_set(:@real_x,gp.x*Game_Map::REAL_RES_X)
    gp.instance_variable_set(:@real_y,gp.y*Game_Map::REAL_RES_Y)
    data[:global_metadata].followers.each do |f|
      next unless f.current_map_id==102
      f.x-=24;f.y-=20
    end
    File.binwrite('legacy-coast.rxdata',Marshal.dump(data))
    gp.instance_variable_set(:@x,17);gp.instance_variable_set(:@y,12)
    data[:global_metadata].followers.each { |f| f.x=16;f.y=12 }
    File.binwrite('legacy-water.rxdata',Marshal.dump(data))
    Tidebound::World.travel_coast(33,20);coast_step('right')
    raise 'pier run' unless Tidebound.story[:walk_state]==:at_pier && [Tidebound::World.actor(:pookie_outside).x,Tidebound::World.actor(:pookie_outside).y]==Tidebound::World.coast_xy(*o::POOKIE_PIER)
    raise 'unseen presence visible' if o.lapras_visible || Tidebound.story[:lapras_glimpsed]
    Tidebound::World.coast_camera_to(*Tidebound::World.coast_xy(53,20));shot('pier');Tidebound::World.coast_camera_home
    raise 'save pier' unless Game.save('coast-pier.rxdata')
    Tidebound::World.travel_coast(52,20);o.pookie;Tidebound::World.travel(:home,10,12);o.home_arrival
    raise 'return home' unless Tidebound.story[:walk_state]==:complete
    o.house_pet(:NATU)
    Tidebound::World.travel_coast(21,12);Tidebound::Interactions.outside_seller;o.forest_gate
    raise 'forest gate' unless $game_map.map_id==103
    o.forest_keys;Tidebound::World.travel_coast(21,12);Tidebound::Interactions.outside_seller
    raise 'seller entry' unless [Tidebound::World.actor(:seller_outside).x,Tidebound::World.actor(:seller_outside).y]==Tidebound::World.coast_xy(21,11)
    Tidebound::Interactions.shop_door;Tidebound::Interactions.oil_seller;Tidebound::World.travel(:home,10,12);Tidebound::Interactions.mother;Tidebound::World.travel(:lantern,6,9);o.main_lamp
    Tidebound::World.travel_coast(53,20);o.pier
    raise 'Lapras scene' unless Tidebound.story[:lapras_glimpsed] && !o.lapras_visible && $tb_lapras_shot
    x,y=Tidebound::World.camera_position($game_player.x,$game_player.y)
    raise 'camera not restored' unless ($game_map.display_x-x).abs<1 && ($game_map.display_y-y).abs<1
    raise 'font config regression' unless File.read('mkxp.json').include?('"fontHeightReporting": 1')
    raise 'save ending' unless Game.save('coast-complete.rxdata')
    File.write('COAST_PASS.txt',"PASS: native coastline, walking, invisible pier reaction/camera, follower saves, keys/shop transfers and fading Lapras scene.\n")
    exit
  rescue Exception => e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('COAST_FAIL.txt',e.full_message);puts e.full_message;exit(1)
  end
end
Scene_Map.prepend(TideboundCoastCheck)
