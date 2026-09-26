# TEST ONLY: full native loads in separate processes. TB_RESUME selects the case.
$stdout.sync=true
$tb_resume_mode=ENV.fetch("TB_RESUME","walking")
module TideboundResumeInput
  def trigger?(key)
    return !$tb_hold_dialog && Graphics.frame_count % 6 == 0 if key==Input::USE
    super
  end
end
Input.singleton_class.prepend(TideboundResumeInput)
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file("#{$tb_resume_mode=="pier_quest" ? "walking" : $tb_resume_mode}.rxdata"))
  end
end
module TideboundRenderedResume
  def update
    super
    return if @tb_resume || !$player || !$game_map
    return if pbMapInterpreterRunning? || $game_temp.message_window_showing
    @tb_resume=true
    o=Tidebound::Opening
    case $tb_resume_mode
    when "walking"
      raise "walk save state" unless Tidebound.story[:walk_steps]==99 && Followers.get(o::POOKIE_FOLLOWER)
      $game_player.move_right
      24.times { Graphics.update; Input.update; update }
      raise "loaded step progress" unless Tidebound.story[:walk_steps]==100
      Tidebound::World.travel(:home,10,12);o.home_arrival
      raise "no-pier route blocked" unless Tidebound.story[:walk_state]==:complete && !Tidebound.story[:walk_pier_seen]
      original=o.household_pets[:POOCHYENA];id=Tidebound.identity(original)
      o.house_pet(:POOCHYENA)
      raise "walked dog changed" unless $player.party.first.equal?(original) && Tidebound.identity($player.party.first)==id
      raise "follower duplicated" if Followers.get(o::POOKIE_FOLLOWER)
      $game_player.moveto(7,7)
      5.times { Graphics.update; updateSpritesets }
      b=Graphics.snap_to_bitmap;b.to_file("final-family.png");b.dispose
      # Capture an actual dialogue window, with complete text, not an offline mock.
      frames=0
      $tb_hold_dialog=true
      pbMessage("Mother: There are things I want to teach you while I still can.") do
        frames+=1
        if frames==80
          b=Graphics.snap_to_bitmap;b.to_file("dialogue-fonts.png");b.dispose
          $tb_hold_dialog=false
        end
      end
      o.household_pets[:POOCHYENA]=original
      Tidebound::World.travel(:coast,10,16)
      # Visual-only reset in this disposable test to inspect the sleeping pose.
      Tidebound.story[:walk_state]=:requested
      5.times { Graphics.update; updateSpritesets }
      b=Graphics.snap_to_bitmap;b.to_file("sleeping-pookie.png");b.dispose
    when "pier_quest"
      raise "walk fixture" unless Tidebound.story[:walk_steps]==99
      Tidebound::World.travel(:coast,33,20)
      $game_player.move_right
      30.times { Graphics.update; Input.update; update }
      raise "pier run" unless Tidebound.story[:walk_state]==:at_pier && Tidebound::World.actor(:pookie_outside).x==45
      raise "save at pier" unless Game.save("pier.rxdata")
      b=Graphics.snap_to_bitmap;b.to_file("pookie-pier.png");b.dispose
      Tidebound::World.travel(:home,10,12);o.home_arrival
      raise "home without dog" unless Tidebound.story[:walk_state]==:at_pier
      Tidebound::World.travel(:coast,44,20);o.pookie;Tidebound::World.travel(:home,10,12);o.home_arrival
      o.house_pet(:MAKUHITA)
      Tidebound::World.travel(:coast,21,12);Tidebound::Interactions.shop_door
      raise "closed shop" unless $game_map.map_id==102
      Tidebound::Interactions.outside_seller;o.forest_gate
      # Use the actual adjacent action event to collect the keys.
      $game_player.moveto(14,12);$game_player.turn_up
      event=Tidebound::World.actor("Shop keys")
      raise "key event cannot interact" if event.over_trigger?
      event.start
      15.times { Graphics.update; Input.update; update }
      raise "key event missing item" unless $bag.has?(:TIDEBOUNDOILKEYS)
      raise "key save" unless Game.save("keys.rxdata")
      Tidebound::World.travel(:coast,21,12);Tidebound::Interactions.outside_seller
      seller=Tidebound::World.actor(:seller_outside)
      raise "seller entry" unless [seller.x,seller.y]==[21,11] && seller.opacity==0 && seller.through
      Tidebound::Interactions.shop_door;Tidebound::Interactions.oil_seller
      b=Graphics.snap_to_bitmap;b.to_file("oil-shop.png");b.dispose
      Tidebound::World.travel(:home,10,12);Tidebound::Interactions.mother;Tidebound::World.travel(:lantern,6,9);o.main_lamp
      raise "lamp continuation" unless Tidebound.story[:lamp_lit]
      raise "final save" unless Game.save("opening-complete.rxdata")
      b=Graphics.snap_to_bitmap;b.to_file("lamp.png");b.dispose
    when "pier"
      raise "waiting position" unless Tidebound.story[:walk_state]==:at_pier && Tidebound::World.actor(:pookie_outside).x==45
      raise "waiting follower duplicate" if Followers.get(o::POOKIE_FOLLOWER)
      o.pookie
      raise "resume following" unless Followers.get(o::POOKIE_FOLLOWER)
    when "keys"
      raise "key item lost" unless $bag.has?(:TIDEBOUNDOILKEYS) && GameData::Item.get(:TIDEBOUNDOILKEYS).is_key_item?
      Tidebound::World.travel(:coast,21,12);Tidebound::Interactions.outside_seller;Tidebound::Interactions.shop_door;Tidebound::Interactions.oil_seller
      raise "key continuation" unless Tidebound.story[:shop_unlocked] && Tidebound.story[:oil_collected] && !$bag.has?(:TIDEBOUNDOILKEYS)
    when "legacy"
      raise "legacy party reset" unless $player.party.first.species==:MAKUHITA && o.household_pets.size==2
      raise "legacy progress lost" unless Tidebound.story[:lamp_lit] && Tidebound.story[:starter_chosen] && Tidebound.story[:opening_revision]==4
      raise "legacy prologue replay" unless Tidebound.story[:walk_state]==:complete && Tidebound.story[:shop_unlocked]
    end
    File.write("RESUME_#{$tb_resume_mode}_PASS.txt", "PASS: full engine load and continuation (#{$tb_resume_mode}).\n")
    exit
  rescue Exception => e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write("RESUME_#{$tb_resume_mode}_FAIL.txt",e.full_message)
    puts e.full_message
    exit(1)
  end
end
Scene_Map.prepend(TideboundRenderedResume)
