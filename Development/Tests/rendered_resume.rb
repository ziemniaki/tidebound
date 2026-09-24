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
      raise "walk save state" unless o.flags[:walk_steps]==99 && Followers.get(o::POOKIE_FOLLOWER)
      $game_player.move_right
      24.times { Graphics.update; Input.update; update }
      raise "loaded step progress" unless o.flags[:walk_steps]==100
      o.travel(101,10,12);o.home_arrival
      raise "no-pier route blocked" unless o.flags[:walk_state]==:complete && !o.flags[:walk_pier_seen]
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
      o.travel(102,10,16)
      # Visual-only reset in this disposable test to inspect the sleeping pose.
      o.flags[:walk_state]=:requested
      5.times { Graphics.update; updateSpritesets }
      b=Graphics.snap_to_bitmap;b.to_file("sleeping-pookie.png");b.dispose
    when "pier_quest"
      raise "walk fixture" unless o.flags[:walk_steps]==99
      o.travel(102,33,20)
      $game_player.move_right
      30.times { Graphics.update; Input.update; update }
      raise "pier run" unless o.flags[:walk_state]==:at_pier && o.actor("Pookie outside").x==45
      raise "save at pier" unless Game.save("pier.rxdata")
      b=Graphics.snap_to_bitmap;b.to_file("pookie-pier.png");b.dispose
      o.travel(101,10,12);o.home_arrival
      raise "home without dog" unless o.flags[:walk_state]==:at_pier
      o.travel(102,44,20);o.pookie;o.travel(101,10,12);o.home_arrival
      o.house_pet(:MAKUHITA)
      o.travel(102,21,12);o.shop_door
      raise "closed shop" unless $game_map.map_id==102
      o.outside_seller;o.forest_gate
      # Use the actual adjacent action event to collect the keys.
      $game_player.moveto(14,12);$game_player.turn_up
      event=o.actor("Shop keys")
      raise "key event cannot interact" if event.over_trigger?
      event.start
      15.times { Graphics.update; Input.update; update }
      raise "key event missing item" unless $bag.has?(:TIDEBOUNDOILKEYS)
      raise "key save" unless Game.save("keys.rxdata")
      o.travel(102,21,12);o.outside_seller
      seller=o.actor("Seller outside")
      raise "seller entry" unless [seller.x,seller.y]==[21,11] && seller.opacity==0 && seller.through
      o.shop_door;o.oil_seller
      b=Graphics.snap_to_bitmap;b.to_file("oil-shop.png");b.dispose
      o.travel(101,10,12);o.mother;o.travel(104,6,9);o.main_lamp
      raise "lamp continuation" unless o.flags[:lamp_lit]
      raise "final save" unless Game.save("opening-complete.rxdata")
      b=Graphics.snap_to_bitmap;b.to_file("lamp.png");b.dispose
    when "pier"
      raise "waiting position" unless o.flags[:walk_state]==:at_pier && o.actor("Pookie outside").x==45
      raise "waiting follower duplicate" if Followers.get(o::POOKIE_FOLLOWER)
      o.pookie
      raise "resume following" unless Followers.get(o::POOKIE_FOLLOWER)
    when "keys"
      raise "key item lost" unless $bag.has?(:TIDEBOUNDOILKEYS) && GameData::Item.get(:TIDEBOUNDOILKEYS).is_key_item?
      o.travel(102,21,12);o.outside_seller;o.shop_door;o.oil_seller
      raise "key continuation" unless o.flags[:shop_unlocked] && o.flags[:oil_collected] && !$bag.has?(:TIDEBOUNDOILKEYS)
    when "legacy"
      raise "legacy party reset" unless $player.party.first.species==:MAKUHITA && o.household_pets.size==2
      raise "legacy progress lost" unless o.flags[:lamp_lit] && o.flags[:starter_chosen] && o.flags[:opening_revision]==4
      raise "legacy prologue replay" unless o.flags[:walk_state]==:complete && o.flags[:shop_unlocked]
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
