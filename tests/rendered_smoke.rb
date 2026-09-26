# TEST ONLY. Inject into a disposable engine copy, never into release Scripts.
$stdout.sync = true
module TideboundAutoInput
  def trigger?(key)
    return !$tb_no_auto_input && Graphics.frame_count % 5 == 0 if key == Input::USE
    super
  end
end
Input.singleton_class.prepend(TideboundAutoInput)
module TideboundRenderedSmoke
  def tb_shot(name)
    5.times { Graphics.update; updateSpritesets }
    b=Graphics.snap_to_bitmap; b.to_file("#{name}.png"); b.dispose
  end
  def tb_step(direction)
    old=[$game_player.x,$game_player.y]
    $game_player.public_send("move_#{direction}")
    24.times { Graphics.update; Input.update; update }
    raise "blocked test step #{direction} at #{old}" if old==[$game_player.x,$game_player.y]
  end
  def update
    super
    return if @tb_smoke_started || !$player || !$game_map || $game_map.map_id != 107
    return unless Tidebound.story[:opening_started]
    return if pbMapInterpreterRunning? || $game_temp.message_window_showing
    @tb_smoke_started = true
    o=Tidebound::Opening
    tb_shot("bedroom")
    puts "RENDERED: start bedroom pet"
    o.bedroom_pet
    puts "RENDERED: mother left bedroom"
    o.bedroom_exit
    puts "RENDERED: transferred hall"
    # Native transfer starts the main hall's autorun. Let the interpreter finish.
    10.times { Graphics.update; Input.update; update }
    raise "hall scene missing" unless Tidebound.story[:hall_talk]
    tb_shot("hall")
    Tidebound::World.travel(:coast,10,16);o.pookie
    $game_player.moveto(8,18)
    $tb_no_auto_input=true
    # Real successful walking; no direct calls to the quest's counter.
    49.times { tb_step("right"); tb_step("left") }
    raise "98 actual steps #{Tidebound.story[:walk_steps]}" unless Tidebound.story[:walk_steps]==98
    # Turns are not movement; a wall bump also must not count.
    $game_player.turn_up; $game_player.turn_down
    $game_player.moveto(10,14);$game_player.move_left
    24.times { Graphics.update; Input.update; update }
    raise "turn/wall counted" unless Tidebound.story[:walk_steps]==98
    $game_player.moveto(8,18);tb_step("right")
    raise "99th step" unless Tidebound.story[:walk_steps]==99
    tb_shot("pookie-following")
    raise "follower not moving" unless Followers.get(o::POOKIE_FOLLOWER).x.between?(7,9)
    raise "following save failed" unless Game.save("walking.rxdata")
    $tb_no_auto_input=false
    Tidebound::World.travel(:home,10,12);o.home_arrival
    raise "early home completes" unless Tidebound.story[:walk_state]==:following
    # Optional pier encounter comes from an actual step into the trigger area.
    Tidebound::World.travel(:coast,33,20)
    tb_step("right")
    raise "pier scene failed" unless Tidebound.story[:walk_state]==:at_pier && Tidebound::World.actor(:pookie_outside).x==45
    tb_shot("pookie-pier")
    raise "pier save failed" unless Game.save("pier.rxdata")
    Tidebound::World.travel(:home,10,12);o.home_arrival
    raise "abandoned Pookie completed walk" unless Tidebound.story[:walk_state]==:at_pier
    Tidebound::World.travel(:coast,44,20);o.pookie
    Tidebound::World.travel(:home,10,12);o.home_arrival
    raise "walk not complete" unless Tidebound.story[:walk_state]==:complete
    tb_shot("family-choice")
    o.house_pet(:MAKUHITA)
    raise "starter identity/party" unless $player.party.first.species==:MAKUHITA && o.household_pets.size==2
    Tidebound::World.travel(:coast,21,12);Tidebound::Interactions.shop_door
    raise "shop early" unless $game_map.map_id==102
    Tidebound::Interactions.outside_seller;tb_shot("locked-shop")
    o.forest_gate;o.forest_keys
    raise "no bag keys" unless $bag.has?(:TIDEBOUNDOILKEYS)
    raise "keys save failed" unless Game.save("keys.rxdata")
    tb_shot("forest-keys")
    Tidebound::World.travel(:coast,21,12);Tidebound::Interactions.outside_seller
    raise "seller not hidden" unless Tidebound::World.actor(:seller_outside).opacity==0 && Tidebound::World.actor(:seller_outside).through
    Tidebound::Interactions.shop_door;Tidebound::Interactions.oil_seller;tb_shot("oil-shop")
    Tidebound::World.travel(:home,10,12);Tidebound::Interactions.mother
    Tidebound::World.travel(:lantern,6,9);o.main_lamp;tb_shot("lamp")
    raise "lamp failed" unless Tidebound.story[:lamp_lit]
    raise "final save failed" unless Game.save("opening-complete.rxdata")
    File.write("RENDERED_PASS.txt", "PASS: native bedroom/hall scenes, actual 99/100 walking, wall/turn exclusion, optional pier run, family choice, bag keys, moving seller, oil/lamp, full saves.\n")
    puts File.read("RENDERED_PASS.txt")
    exit
  rescue Exception => e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write("RENDERED_FAILURE.txt",e.full_message)
    puts e.full_message
    exit(1)
  end
end
Scene_Map.prepend(TideboundRenderedSmoke)
