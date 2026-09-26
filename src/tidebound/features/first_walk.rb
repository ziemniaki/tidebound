# The household walk and companion choice.
module Tidebound
  module Opening
    POOKIE_FOLLOWER = "Tidebound Pookie"
    POOKIE_PIER = [53, 20].freeze
    WALK_LENGTH = 100
    module_function

    def bedroom_pet
      if Tidebound.story[:bedroom_talk]
        pbMessage("Wick taps twice against the floor. The old game can wait.")
        return
      end
      pbMessage("You hide a button in your palm. Wick chooses the right hand. He always does.")
      visitor = Tidebound::World.actor(:mother_visiting)
      visitor.opacity = 255 if visitor
      Tidebound::World.animate(visitor, [PBMoveRoute::CHANGE_SPEED, 3, PBMoveRoute::UP, PBMoveRoute::UP])
      pbMessage("Mother: There you are, you two.")
      pbMessage("Mother: We need to talk, love. Come down to the main hall, will you?")
      Tidebound::World.animate(visitor, [PBMoveRoute::DOWN, PBMoveRoute::DOWN])
      visitor.opacity = 0 if visitor
      visitor.through = true if visitor
      Tidebound.story[:bedroom_talk] = true
    end

    def bedroom_exit
      bedroom_pet unless Tidebound.story[:bedroom_talk]
      Tidebound::World.travel(:home, 6, 4, 2)
    end

    def home_arrival
      Tidebound::World.erase_autorun
      unless Tidebound.story[:opening_started]
        Tidebound::World.travel(:bedroom, 6, 8, 6)
        return
      end
      unless Tidebound.story[:hall_talk]
        hall_talk
        return
      end
      if Tidebound.story[:walk_state] == :following && Tidebound.story[:walk_steps].to_i >= WALK_LENGTH
        finish_walk
      end
    end

    def hall_talk
      return if Tidebound.story[:hall_talk]
      Tidebound::World.animate($game_player, [PBMoveRoute::DOWN, PBMoveRoute::DOWN, PBMoveRoute::DOWN, PBMoveRoute::RIGHT, PBMoveRoute::TURN_RIGHT])
      maku = Tidebound::World.actor(:house_makuhita)
      crate = Tidebound::World.actor(:crate)
      Tidebound::World.animate(crate, [PBMoveRoute::CHANGE_SPEED, 3, PBMoveRoute::DOWN])
      Tidebound::World.animate(maku, [PBMoveRoute::CHANGE_SPEED, 3, PBMoveRoute::DOWN])
      pbMessage("Mother: Sit a moment, love. I've been thinking.")
      pbMessage("Mother: You've grown old enough to go outside on your own. To see something beyond our windows.")
      Tidebound::World.animate(crate, [PBMoveRoute::JUMP, 1, 0])
      Tidebound::World.animate(maku, [PBMoveRoute::TURN_RIGHT])
      pbMessage("Mother: Oh, Maku! Gently, sweetheart. Those are bottles, not turnips.")
      pbMessage("Maku pats the box twice, very carefully.")
      Tidebound::World.animate(maku, [PBMoveRoute::JUMP, 0, 0])
      pbMessage("Mother: You have such a good heart. Now, where was I?")
      pbMessage("Mother: There are things I want to teach you. I haven't as much time as I once had.")
      pbMessage("She smooths a crease in your sleeve that isn't there.")
      pbMessage("Mother: Why don't you take Pookie for a walk? She's asleep just outside the lighthouse.")
      pbMessage("Mother: A hundred little steps around the village. Then come home together. We'll take it from there.")
      Tidebound.story[:hall_talk] = true
      Tidebound.story[:walk_state] = :requested
    end

    def pookie
      case Tidebound.story[:walk_state]
      when :not_started, nil
        pbMessage("Pookie sleeps with her nose tucked beneath her tail.")
      when :requested
        pbMessage("Pookie opens one eye. Then she sees you reaching for her walking ribbon.")
        pbMessage("She springs up, tail wagging. For once, Mother isn't coming too.")
        start_following
      when :at_pier
        pbMessage("Pookie stands rigid at the end of the pier. Her growl is so low you can feel it through the boards.")
        pbMessage("You look down. Nothing. Only water, black beneath the posts.")
        pbMessage("You say her name. Slowly, she turns back to you.")
        start_following
      end
    end

    def start_following
      dog = Tidebound::World.actor(:pookie_outside)
      return unless dog
      Followers.add(dog.id, POOKIE_FOLLOWER, nil) unless Followers.get(POOKIE_FOLLOWER)
      Tidebound.story[:walk_state] = :following
      Tidebound.story[:walk_distance] = $stats.distance_walked
      dog.through = true
      pbMessage("Pookie is following you. Walk 100 steps outside, then return home together.") unless Tidebound.story[:walk_instructions]
      Tidebound.story[:walk_instructions] = true
    end

    def walk_step
      return unless Tidebound.story[:walk_state] == :following
      previous_distance = Tidebound.story[:walk_distance]
      Tidebound.story[:walk_distance] = $stats.distance_walked
      # Essentials also emits this hook for its wall-bump animation. Its actual
      # distance statistic changes only when a move succeeds, not on a bump.
      return unless previous_distance && $stats.distance_walked > previous_distance
      return unless $game_map.map_id == 102
      return unless Followers.get(POOKIE_FOLLOWER)
      Tidebound.story[:walk_steps] = [Tidebound.story[:walk_steps].to_i + 1, WALK_LENGTH].min
      if !Tidebound.story[:walk_pier_seen] && (34..38).include?($game_player.x - World::COAST_OFFSET[0]) && (19..21).include?($game_player.y - World::COAST_OFFSET[1])
        Tidebound.story[:walk_pier_pending] = true
      end
    end

    def walk_frame
      return if @walk_scene_busy
      return unless $game_map && $game_map.map_id == 102
      return unless Tidebound.story[:walk_state] == :following
      return if pbMapInterpreterRunning? || $game_temp.message_window_showing || $game_temp.in_menu || $game_player.moving?
      return unless Tidebound.story[:walk_pier_pending] || (Tidebound.story[:walk_steps].to_i >= WALK_LENGTH && !Tidebound.story[:walk_ready_told])
      # Miniupdates used by messages/pbWait already suppress player input.
      # Do not set in_menu: Essentials also freezes NPC movement in a menu.
      @walk_scene_busy = true
      begin
        if Tidebound.story[:walk_pier_pending]
          pier_run
        else
          Tidebound.story[:walk_ready_told] = true
          pbMessage("Pookie has had her hundred steps. Time to go home together.")
        end
      ensure
        @walk_scene_busy = false
      end
    end

    def pier_run
      dog = Tidebound::World.actor(:pookie_outside)
      follower = Followers.get(POOKIE_FOLLOWER)
      return unless dog && follower
      Tidebound.story[:walk_pier_pending] = false
      Tidebound.story[:walk_pier_seen] = true
      dog.moveto(follower.x, follower.y)
      Followers.remove(POOKIE_FOLLOWER)
      Tidebound.story[:walk_state] = :running
      Pokemon.play_cry(:POOCHYENA)
      pbMessage("Pookie stops. Her ears flatten.")
      pbMessage("A sharp bark. She tears away towards the end of the pier.")
      # This branch begins on the open pier approach, never across buildings.
      route = [PBMoveRoute::CHANGE_SPEED, 4]
      route += [dog.y < Tidebound::World.coast_xy(*POOKIE_PIER)[1] ? PBMoveRoute::DOWN : PBMoveRoute::UP] * (dog.y - Tidebound::World.coast_xy(*POOKIE_PIER)[1]).abs
      route += [PBMoveRoute::RIGHT] * [Tidebound::World.coast_xy(*POOKIE_PIER)[0] - dog.x, 0].max
      route += [PBMoveRoute::TURN_DOWN]
      Tidebound::World.coast_camera_target = dog
      Tidebound::World.animate(dog, route)
      Tidebound::World.coast_camera_target = nil
      Tidebound.story[:walk_state] = :at_pier
      dog.through = false
      pbWait(0.45)
      pbMessage("Only the tide beneath the boards. You cannot see what she is barking at.")
      Tidebound::World.coast_camera_home
    ensure
      Tidebound::World.coast_camera_target = nil
    end

    def finish_walk
      return unless Tidebound.story[:walk_state] == :following && Tidebound.story[:walk_steps].to_i >= WALK_LENGTH
      Followers.remove(POOKIE_FOLLOWER)
      Tidebound.story[:walk_state] = :complete
      Tidebound.story[:walk_pier_pending] = false
      pbMessage("Pookie shakes the sea air from her coat. Wick hops down to greet you; Maku sets his box aside.")
      pbMessage("Mother: There you are. Both of you.")
      pbMessage("She counts your fingers with her thumb, then catches herself and lets go.")
      Interactions.mother
    end

    def unlock_shop
      unless Tidebound.story[:oil_requested]
        pbMessage("Seller: Locked myself out again. Never mind me, little one. Enjoy your morning.")
        return
      end
      if Tidebound.story[:shop_unlocked]
        pbMessage("Seller: Come inside. Your mother's bottle is waiting.")
      elsif $bag.has?(:TIDEBOUNDOILKEYS)
        pbMessage("Seller: My keys! I knew I shouldn't have put them down.")
        $bag.remove(:TIDEBOUNDOILKEYS, 1)
        Tidebound.story[:shop_unlocked] = true
        seller = Tidebound::World.actor(:seller_outside)
        pbMessage("He works the stiff lock until it gives.")
        Tidebound::World.animate(seller, [PBMoveRoute::CHANGE_SPEED, 3, PBMoveRoute::LEFT, PBMoveRoute::UP])
        seller.opacity = 0 if seller
        seller.through = true if seller
        pbMessage("Seller: Come in, come in. Let's get you that oil.")
      else
        Tidebound.story[:keys_requested] = true
        pbMessage("Seller: Your mother's oil? It's ready, only... I've lost the keys again.")
        pbMessage("Seller: In the wood up north. I stopped by those little white flowers. I think I set them down there.")
        pbMessage("Seller: Will you look? My knees aren't what they were. Stay clear of the dark pool.")
      end
    end

    def enter_shop
      if Tidebound.story[:shop_unlocked]
        Tidebound::World.travel(:shop, 8, 10, 8)
      else
        pbMessage("The oil-shop door is locked. The seller is standing beside it.")
        $game_player.moveto(*Tidebound::World.coast_xy(21, 12))
        $game_player.turn_down
      end
    end

    def forest_keys
      return if Tidebound.story[:shop_unlocked] || Tidebound.story[:keys_collected]
      unless Tidebound.story[:keys_requested]
        pbMessage("Something brass is caught beneath the white flowers.")
        return
      end
      unless $bag.add(:TIDEBOUNDOILKEYS, 1)
        pbMessage("There is no room in the Key Items pocket. The keys are still here.")
        return
      end
      Tidebound.story[:keys_collected] = true
      pbMessage("A ring of old brass keys lies beneath the flowers. One has a tiny oil bottle scratched into it.")
      pbMessage("You put the Oil-Shop Keys in the Key Items pocket.")
    end

    def sync_opening_actors
      return unless MAP_IDS.include?($game_map.map_id)
      seller = Tidebound::World.actor(:seller_outside)
      if seller
        seller.opacity = Tidebound.story[:shop_unlocked] ? 0 : 255
        seller.through = !!Tidebound.story[:shop_unlocked]
      end
      dog = Tidebound::World.actor(:pookie_outside)
      dog.moveto(*Tidebound::World.coast_xy(*POOKIE_PIER)) if dog && Tidebound.story[:walk_state] == :at_pier
      visitor = Tidebound::World.actor(:mother_visiting)
      if visitor
        visitor.opacity = 0
        visitor.through = true
      end
    end
  end
end

EventHandlers.add(:on_player_step_taken, :tidebound_pookie_steps,
  proc { Tidebound::Opening.walk_step })
EventHandlers.add(:on_frame_update, :tidebound_pookie_scene,
  proc { Tidebound::Opening.walk_frame })
EventHandlers.add(:on_new_spriteset_map, :tidebound_opening_actors,
  proc { |_spriteset, _viewport| Tidebound::Opening.sync_opening_actors })
