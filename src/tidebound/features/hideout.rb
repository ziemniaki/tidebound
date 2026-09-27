# Storehouse quest, guard battle and Mending minigame.
module Tidebound::Hideout
  module_function
  def q
    Tidebound::NeighborQuest.q
  end
  def say(*s)
    Tidebound::NeighborQuest.say(*s)
  end
  def active?
    Tidebound::NeighborQuest.stage == :pursuit
  end
  def actor
    Tidebound::World.actor(:necklace_thief)
  end
  def sync
    return unless $game_map && $game_map.map_id == 109
    e = actor
    return unless e
    seated = !q[:second_won] && !%i[necklace complete].include?(q[:stage])
    e.character_name = seated ? "ivo" : "trainer_CAMPER"
    e.instance_variable_set(:@direction_fix, seated)
    e.instance_variable_set(:@step_anime, false)
    e.moveto(13, 4) unless seated
    e.turn_down unless seated
  end
  def arrival
    sync
    Tidebound::World.erase_autorun
    return unless active? && !q[:heard]
    say(
      "You step around a bowl with something growing in it.",
      "Bram: Boss said no more taking things from houses.",
      "Ivo: It was a SHOP. And stop talking. I am nearly through this bit.",
      "Packer: How much do pearls go for?",
      "Bram: Depends on the pearl, probably.",
      "Packer: Shall I send them with the boxes?",
      "Bram: People at the docks buy anything from the coast. Let them work it out.",
      "Lookout: Our first proper Team Abyss job and nobody bought a broom."
    )
    q[:heard] = true
  end
  def clutter
    say(
      "Empty bowls, stale crusts, damp socks and shipping wrappers.",
      "A note says: YOUR TURN TO TIDY. Three different names have been crossed out."
    )
  end
  def guard
    unless active? && !q[:runner_won]
      return say("Bram: He lost. Twice. I would leave him alone for a bit.")
    end
    return unless Tidebound::Encounters.able?
    say(
      "Bram: Whoa. Quiet. He is playing.",
      "Bram: Last time somebody stood in front of the glass, he made us start from the beginning.",
      "Bram: You want to bother him? Get past me first."
    )
    return unless Tidebound::NeighborQuest.battle(:runner) == 1
    q[:runner_won] = true
    say("Bram: All right. Your funeral. Just do not step on the handpiece.")
  end
  def approach
    return unless active? && !q[:runner_won]
    guard
    # Cancel/no able party must never let a player walk through the guard line.
    if $game_map.map_id == 109 && !q[:runner_won]
      $game_player.moveto($game_player.x, 10)
      $game_player.turn_up
    end
  end
  def play
    result = false
    pbFadeOutIn { result = Scene_TideboundMending.new.main }
    result
  ensure
    $game_map.autoplay if $game_map && $game_map.map_id == 109
    Input.update
  end
  def console
    return boss if active?
    say("The little glass has gone dark. A thumbprint remains over the last rune.")
  end
  def cache
    return handoff if active? && q[:second_won]
    say("A cupboard of odd gloves, bent cutlery and things somebody meant to sell.")
  end
  def boss
    unless active?
      say(
        "Ivo: I should not have taken it.",
        "Ivo: I know. I am not asking you to say it is all right."
      )
      return
    end
    unless q[:runner_won]
      approach
      return
    end
    unless q[:second_won]
      unless q[:hideout_game_won]
        say(
          "Ivo does not look away from the little glass.",
          "Ivo: The necklace? Beat my game first. Then I might remember where I put it."
        )
        return unless pbConfirmMessage("Take the handpiece?")
        say("The wooden handpiece is warm. There are two worn thumb-stones.")
        unless play
          say("Ivo: Giving up? It is only a game.")
          return
        end
        q[:hideout_game_won] = true
        say(
          "The room returns. A spoon falls from the sofa.",
          "Ivo: No. That does not count. You must have played it before.",
          "Ivo: Fine. A REAL battle. Then we will see."
        )
      else
        say("Ivo: Yes, yes. You beat the game. You still have to beat me.")
      end
      return unless Tidebound::Encounters.able?
      e = actor
      if e
        e.character_name = "trainer_CAMPER"
        e.instance_variable_set(:@direction_fix, false)
        e.turn_toward_player
      end
      result = Tidebound::NeighborQuest.battle(:second)
      unless result == 1
        sync
        return
      end
      q[:second_won] = true
      say(
        "Ivo: ...I said I would tell you.",
        "Ivo: He is a decent old man. I knew that when I took it.",
        "Ivo: Come here. I put it away from this mess."
      )
      lead_to_cache
      follow_to_cache
    end
    handoff
  end
  def lead_to_cache
    e = actor
    return unless e
    # The short route crosses a possible player interaction tile. Restore
    # collision afterward; never leave an invisible or through door blocker.
    through = e.through
    e.through = true
    Tidebound::World.animate(
      e,
      [
        PBMoveRoute::DOWN,
        PBMoveRoute::LEFT,
        PBMoveRoute::LEFT,
        PBMoveRoute::LEFT,
        PBMoveRoute::UP,
        PBMoveRoute::TURN_LEFT
      ]
    )
  ensure
    if e
      e.moveto(13, 4)
      e.through = through
      e.instance_variable_set(:@direction_fix, false)
      e.turn_left
    end
  end
  def handoff
    return unless active? && q[:second_won]
    unless $bag.has?(Tidebound::NeighborQuest::NECKLACE) ||
             $bag.add(Tidebound::NeighborQuest::NECKLACE, 1)
      say("Ivo: Make room in your bag. I will keep it in this cupboard. No more games.")
      return
    end
    q[:stage] = :necklace
    sync
    say(
      "Ivo opens a small cloth bundle. The pearls are all there.",
      "Ivo: Here. Take it back to him. Tell him... No. I ought to tell him myself.",
      "You put the Pearl Necklace carefully in the Key Items pocket."
    )
  end
  def follow_to_cache
    return unless $game_map.map_id == 109
    mask = Tidebound::MAP_PASSAGES[109]
    blocked = $game_map.events.values.reject(&:through).map { |e| [e.x, e.y] }
    start = [$game_player.x, $game_player.y]
    todo = [[start, []]]
    seen = { start => true }
    directions = [
      [1, 0, PBMoveRoute::RIGHT],
      [-1, 0, PBMoveRoute::LEFT],
      [0, 1, PBMoveRoute::DOWN],
      [0, -1, PBMoveRoute::UP]
    ]
    until todo.empty?
      cell, route = todo.shift
      if cell == [13, 5]
        Tidebound::World.animate($game_player, route + [PBMoveRoute::TURN_UP])
        return
      end
      directions.each do |dx, dy, command|
        x = cell[0] + dx
        y = cell[1] + dy
        p = [x, y]
        next if x < 0 || y < 0 || !mask[y] || mask[y][x] != "1" || blocked.include?(p) || seen[p]
        seen[p] = true
        todo << [p, route + [command]]
      end
    end
  end
end

EventHandlers.add(
  :on_new_spriteset_map,
  :tidebound_hideout,
  proc { |_s, _v| Tidebound::Hideout.sync }
)
