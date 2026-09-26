# Opening revision 4. Story flags and native follower data survive ordinary saves.
module Tidebound
  module Opening
    POOKIE_FOLLOWER = "Tidebound Pookie"
    WALK_LENGTH = 100
    module_function

    def actor(name)
      $game_map.events.values.find { |event| event.name == name }
    end

    # Essentials' pbMoveRoute schedules a route; its wait argument does not wait.
    def animate(event, commands)
      return unless event
      previous_through = event.through
      pbMoveRoute(event, commands)
      deadline = System.uptime + 20
      while event.move_route_forcing
        raise "Tidebound: scene movement timed out" if System.uptime > deadline
        pbWait(0.025)
      end
      # Essentials appends THROUGH_OFF even for actors which were already through.
      event.through = previous_through
    end

    def bedroom_pet
      if flags[:bedroom_talk]
        pbMessage("Wick taps twice against the floor. The old game can wait.")
        return
      end
      pbMessage("You hide a button in your palm. Wick chooses the right hand. He always does.")
      visitor = actor("Mother visiting")
      visitor.opacity = 255 if visitor
      animate(visitor, [PBMoveRoute::CHANGE_SPEED, 3, PBMoveRoute::UP, PBMoveRoute::UP])
      pbMessage("Mother: There you are, you two.")
      pbMessage("Mother: We need to talk, love. Come down to the main hall, will you?")
      animate(visitor, [PBMoveRoute::DOWN, PBMoveRoute::DOWN])
      visitor.opacity = 0 if visitor
      visitor.through = true if visitor
      flags[:bedroom_talk] = true
    end

    def bedroom_exit
      bedroom_pet unless flags[:bedroom_talk]
      travel(101, 6, 4, 2)
    end

    def home_arrival
      erase_autorun
      migrate_opening!
      unless flags[:opening_started]
        travel(107, 6, 8, 6)
        return
      end
      unless flags[:hall_talk]
        hall_talk
        return
      end
      if flags[:walk_state] == :following && flags[:walk_steps].to_i >= WALK_LENGTH
        finish_walk
      end
    end

    def hall_talk
      return if flags[:hall_talk]
      animate($game_player, [PBMoveRoute::DOWN, PBMoveRoute::DOWN, PBMoveRoute::DOWN, PBMoveRoute::RIGHT, PBMoveRoute::TURN_RIGHT])
      maku = actor("House:MAKUHITA")
      crate = actor("Crate")
      animate(crate, [PBMoveRoute::CHANGE_SPEED, 3, PBMoveRoute::DOWN])
      animate(maku, [PBMoveRoute::CHANGE_SPEED, 3, PBMoveRoute::DOWN])
      pbMessage("Mother: Sit a moment, love. I've been thinking.")
      pbMessage("Mother: You've grown old enough to go outside on your own. To see something beyond our windows.")
      animate(crate, [PBMoveRoute::JUMP, 1, 0])
      animate(maku, [PBMoveRoute::TURN_RIGHT])
      pbMessage("Mother: Oh, Maku! Gently, sweetheart. Those are bottles, not turnips.")
      pbMessage("Maku pats the box twice, very carefully.")
      animate(maku, [PBMoveRoute::JUMP, 0, 0])
      pbMessage("Mother: You have such a good heart. Now, where was I?")
      pbMessage("Mother: There are things I want to teach you. I haven't as much time as I once had.")
      pbMessage("She smooths a crease in your sleeve that isn't there.")
      pbMessage("Mother: Why don't you take Pookie for a walk? She's asleep just outside the lighthouse.")
      pbMessage("Mother: A hundred little steps around the village. Then come home together. We'll take it from there.")
      flags[:hall_talk] = true
      flags[:walk_state] = :requested
    end

    def pookie
      case flags[:walk_state]
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
      dog = actor("Pookie outside")
      return unless dog
      Followers.add(dog.id, POOKIE_FOLLOWER, nil) unless Followers.get(POOKIE_FOLLOWER)
      flags[:walk_state] = :following
      flags[:walk_distance] = $stats.distance_walked
      dog.through = true
      pbMessage("Pookie is following you. Walk 100 steps outside, then return home together.") unless flags[:walk_instructions]
      flags[:walk_instructions] = true
    end

    def walk_step
      return unless flags[:walk_state] == :following
      previous_distance = flags[:walk_distance]
      flags[:walk_distance] = $stats.distance_walked
      # Essentials also emits this hook for its wall-bump animation. Its actual
      # distance statistic changes only when a move succeeds, not on a bump.
      return unless previous_distance && $stats.distance_walked > previous_distance
      return unless $game_map.map_id == 102
      return unless Followers.get(POOKIE_FOLLOWER)
      flags[:walk_steps] = [flags[:walk_steps].to_i + 1, WALK_LENGTH].min
      if !flags[:walk_pier_seen] && (34..38).include?($game_player.x - COAST_OFFSET[0]) && (19..21).include?($game_player.y - COAST_OFFSET[1])
        flags[:walk_pier_pending] = true
      end
    end

    def walk_frame
      return if @walk_scene_busy
      return unless $game_map && $game_map.map_id == 102
      return unless flags[:walk_state] == :following
      return if pbMapInterpreterRunning? || $game_temp.message_window_showing || $game_temp.in_menu || $game_player.moving?
      return unless flags[:walk_pier_pending] || (flags[:walk_steps].to_i >= WALK_LENGTH && !flags[:walk_ready_told])
      # Miniupdates used by messages/pbWait already suppress player input.
      # Do not set in_menu: Essentials also freezes NPC movement in a menu.
      @walk_scene_busy = true
      begin
        if flags[:walk_pier_pending]
          pier_run
        else
          flags[:walk_ready_told] = true
          pbMessage("Pookie has had her hundred steps. Time to go home together.")
        end
      ensure
        @walk_scene_busy = false
      end
    end

    def pier_run
      dog = actor("Pookie outside")
      follower = Followers.get(POOKIE_FOLLOWER)
      return unless dog && follower
      flags[:walk_pier_pending] = false
      flags[:walk_pier_seen] = true
      dog.moveto(follower.x, follower.y)
      Followers.remove(POOKIE_FOLLOWER)
      flags[:walk_state] = :running
      Pokemon.play_cry(:POOCHYENA)
      pbMessage("Pookie stops. Her ears flatten.")
      pbMessage("A sharp bark. She tears away towards the end of the pier.")
      # This branch begins on the open pier approach, never across buildings.
      route = [PBMoveRoute::CHANGE_SPEED, 4]
      route += [dog.y < coast_xy(*POOKIE_PIER)[1] ? PBMoveRoute::DOWN : PBMoveRoute::UP] * (dog.y - coast_xy(*POOKIE_PIER)[1]).abs
      route += [PBMoveRoute::RIGHT] * [coast_xy(*POOKIE_PIER)[0] - dog.x, 0].max
      route += [PBMoveRoute::TURN_DOWN]
      self.coast_camera_target = dog
      animate(dog, route)
      self.coast_camera_target = nil
      flags[:walk_state] = :at_pier
      dog.through = false
      pbWait(0.45)
      pbMessage("Only the tide beneath the boards. You cannot see what she is barking at.")
      coast_camera_home
    ensure
      self.coast_camera_target = nil
    end

    def finish_walk
      return unless flags[:walk_state] == :following && flags[:walk_steps].to_i >= WALK_LENGTH
      Followers.remove(POOKIE_FOLLOWER)
      flags[:walk_state] = :complete
      flags[:walk_pier_pending] = false
      pbMessage("Pookie shakes the sea air from her coat. Wick hops down to greet you; Maku sets his box aside.")
      pbMessage("Mother: There you are. Both of you.")
      pbMessage("She counts your fingers with her thumb, then catches herself and lets go.")
      mother
    end

    def outside_seller
      unless flags[:oil_requested]
        pbMessage("Seller: Locked myself out again. Never mind me, little one. Enjoy your morning.")
        return
      end
      if flags[:shop_unlocked]
        pbMessage("Seller: Come inside. Your mother's bottle is waiting.")
      elsif $bag.has?(:TIDEBOUNDOILKEYS)
        pbMessage("Seller: My keys! I knew I shouldn't have put them down.")
        $bag.remove(:TIDEBOUNDOILKEYS, 1)
        flags[:shop_unlocked] = true
        seller = actor("Seller outside")
        pbMessage("He works the stiff lock until it gives.")
        animate(seller, [PBMoveRoute::CHANGE_SPEED, 3, PBMoveRoute::LEFT, PBMoveRoute::UP])
        seller.opacity = 0 if seller
        seller.through = true if seller
        pbMessage("Seller: Come in, come in. Let's get you that oil.")
      else
        flags[:keys_requested] = true
        pbMessage("Seller: Your mother's oil? It's ready, only... I've lost the keys again.")
        pbMessage("Seller: In the wood up north. I stopped by those little white flowers. I think I set them down there.")
        pbMessage("Seller: Will you look? My knees aren't what they were. Stay clear of the dark pool.")
      end
    end

    def shop_door
      if flags[:shop_unlocked]
        travel(106, 8, 10, 8)
      else
        pbMessage("The oil-shop door is locked. The seller is standing beside it.")
        $game_player.moveto(*coast_xy(21, 12))
        $game_player.turn_down
      end
    end

    def forest_keys
      return if flags[:shop_unlocked] || flags[:keys_collected]
      unless flags[:keys_requested]
        pbMessage("Something brass is caught beneath the white flowers.")
        return
      end
      unless $bag.add(:TIDEBOUNDOILKEYS, 1)
        pbMessage("There is no room in the Key Items pocket. The keys are still here.")
        return
      end
      flags[:keys_collected] = true
      pbMessage("A ring of old brass keys lies beneath the flowers. One has a tiny oil bottle scratched into it.")
      pbMessage("You put the Oil-Shop Keys in the Key Items pocket.")
    end

    def sync_opening_actors
      return unless MAP_IDS.include?($game_map.map_id)
      migrate_opening!
      seller = actor("Seller outside")
      if seller
        seller.opacity = flags[:shop_unlocked] ? 0 : 255
        seller.through = !!flags[:shop_unlocked]
      end
      dog = actor("Pookie outside")
      dog.moveto(*coast_xy(*POOKIE_PIER)) if dog && flags[:walk_state] == :at_pier
      visitor = actor("Mother visiting")
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
