# Tidebound opening, Essentials 21.1. These scripts are embedded before Main.
module Tidebound
  module Opening
    HOUSE_PETS = {
      NATU: ["Wick", %i[PECK LEER NIGHTSHADE]],
      MAKUHITA: ["Maku", %i[TACKLE ARMTHRUST SANDATTACK FORESIGHT]],
      POOCHYENA: ["Pookie", %i[TACKLE HOWL SANDATTACK BITE]]
    }.freeze
    module_function

    def household_pets
      Tidebound.story[:household_pets] ||= {}
    end

    def begin_story
      Tidebound::World.erase_autorun
      return if Tidebound.story[:opening_started]
      Tidebound.story[:opening_started] = true
      Tidebound.story[:psychic_maze] = :active if $game_map.map_id == 114
      Tidebound.story[:dream_room] = { phase: :sealed, streak: 0 } if $game_map.map_id == 115
      pbChangePlayer(1)
      $player.name = "Ren" # Temporary protagonist name, editable in the journal.
      $player.has_pokedex = false
      $player.has_running_shoes = true
      $player.money = 0
      # 0.7.13 evolution-testing supply; begin_story runs only for a new journey.
      $bag.add(:RARECANDY, 99)
      $PokemonGlobal.pokecenterMapId = -1
      HOUSE_PETS.each do |species, (name, moves)|
        pet = Pokemon.new(species, 7, $player)
        pet.name = name
        pet.gender = species == :POOCHYENA ? 1 : 0
        pet.moves.clear
        moves.each { |move| pet.learn_move(move) }
        Tidebound.state.assign_identity(pet)
        household_pets[species] = pet
      end
      # Home is a safe initial return point; Mother never fully heals the party.
      Tidebound.state.checkpoint = [101, 6, 10, 2]
      Tidebound.story[:walk_state] = :not_started
      Tidebound.story[:walk_steps] = 0
      if $game_map.map_id == 115
        pbMessage("A room. Your room, probably.")
      elsif Tidebound.story[:psychic_maze] == :active
        pbMessage(
          "You tap twice against the blanket. Somewhere beyond the shelves, Wick taps back."
        )
        pbMessage("One more game. Find Wick.")
      else
        pbMessage("Wick hops across your blanket. You tap twice; he taps back.")
        pbMessage("Outside, the lamp turns. In here, it is still your little world.")
        pbMessage("Wick is waiting for your next move. Speak to him with the action button.")
      end
    end

    def mother_dialogue
      unless Tidebound.story[:hall_talk]
        hall_talk
        return
      end
      unless Tidebound.story[:walk_state] == :complete
        if Tidebound.story[:walk_state] == :at_pier
          pbMessage("Mother: Where is Pookie, love? Don't leave her out there alone.")
        elsif Tidebound.story[:walk_state] == :following && Tidebound.story[:walk_steps].to_i >= 100
          finish_walk
        elsif Tidebound.story[:walk_state] == :following
          pbMessage("Mother: A little longer, love. She has been waiting all morning.")
          pbMessage("Pookie's walk: #{Tidebound.story[:walk_steps]}/100 steps outside.")
        else
          pbMessage(
            "Mother: Pookie is asleep beside the lighthouse. Take her for a little walk around the village."
          )
        end
        return
      end
      unless Tidebound.story[:starter_chosen]
        Tidebound.story[:choice_explained] = true
        pbMessage(
          "Mother: It isn't safe to travel alone. One of our little family should go with you."
        )
        pbMessage(
          "Mother: Wick, Maku, or Pookie. Ask whichever one you want beside you. The others will keep me company."
        )
        return
      end
      if !Tidebound.story[:oil_requested]
        Tidebound.story[:oil_requested] = true
        pbMessage(
          "Mother: Before you go far, will you fetch the lamp oil? The little shop beyond the tower keeps a bottle for us."
        )
        pbMessage(
          "Mother: There are things I want to teach you while I still can. The light is one of them."
        )
      elsif Tidebound.story[:oil_collected] && !Tidebound.story[:oil_returned]
        Tidebound.story[:oil_returned] = true
        pbMessage("She takes the bottle in both hands. For a moment, neither of you lets go.")
        pbMessage("Mother: Thank you. Come, you should know how to tend it yourself.")
        pbMessage("She shows you the measure on the bottle and how to trim the wick.")
        pbMessage("Mother: Take it upstairs to the great lamp. Only that one, please.")
      elsif Tidebound.story[:oil_returned] && !Tidebound.story[:lamp_lit]
        pbMessage("Mother: The great lamp, upstairs. Pour to the line, then turn the brass wheel.")
      elsif Tidebound.story[:lamp_lit]
        if Tidebound.state.journey > 0
          pbMessage("Mother: You're cold.")
          pbMessage("She starts to say something else. Instead, she closes the latch.")
        else
          pbMessage("Mother: And come home when you can. I'll leave the latch loose.")
        end
      else
        pbMessage("Mother: Ask the oil seller beyond the tower. Watch the wet steps, both of you.")
      end
    end

    def main_lamp
      if Tidebound.story[:lamp_lit]
        pbMessage("The great lamp turns.\nFor a moment, the sea has an edge.")
      elsif !Tidebound.story[:oil_returned]
        pbMessage("The flame has grown thin. Mother will know what it needs.")
      else
        pbMessage("You pour to the line, trim the wick and turn the brass wheel.")
        Tidebound.story[:lamp_lit] = true
        pbMessage("The flame steadies. Beyond the glass, a strip of water becomes silver.")
        pbMessage(
          "Mother calls from below: That's it, love. Now you know how to bring the light back."
        )
      end
    end

    def house_pet(species)
      pet = household_pets[species]
      return unless pet
      description = {
        NATU: "Wick tilts his head before you speak, as though he remembers the question.",
        MAKUHITA:
          "Maku leans against your knee. He has always carried the heavy things for Mother.",
        POOCHYENA:
          "Pookie presses her nose into your palm. She will not look at the sea-facing window."
      }
      pbMessage(description[species])
      return if Tidebound.story[:starter_chosen]
      unless Tidebound.story[:walk_state] == :complete
        pbMessage("For now, there is a little walk to take together.")
        return
      end
      Interactions.mother unless Tidebound.story[:choice_explained]
      Tidebound.story[:choice_explained] = true
      return unless pbConfirmMessage("Ask #{pet.name}, the #{pet.speciesName}, to come with you?")
      # Keep this individual, including identity and stats, rather than rolling a new one.
      pet.owner = Pokemon::Owner.new_from_trainer($player)
      $player.party << pet
      household_pets.delete(species)
      Tidebound.story[:starter_chosen] = species
      $bag.add(:POKEBALL, 8)
      pbMessage("#{pet.name} settles beside you. This time, you are going together.")
      pbMessage("Mother gives you eight Poké Balls, wrapped in a clean handkerchief.")
      Interactions.mother
    end

    def collect_oil
      unless $game_map.map_id == 106 && Tidebound.story[:shop_unlocked]
        pbMessage("The bottle is inside the locked shop.")
        return
      end
      unless Tidebound.story[:oil_requested]
        pbMessage("Seller: Your mother has been keeping late hours. Go and see her, will you?")
        return
      end
      if Tidebound.story[:oil_collected]
        pbMessage("Seller: I used to sell enough oil to keep three boats going.")
        pbMessage("Seller: The empty bottles make a lovely sound when the wind gets in.")
        return
      end
      Tidebound.story[:oil_collected] = true
      pbMessage("Seller: The keeper's bottle. Already paid for.")
      pbMessage("You take the lamp oil. The glass is wrapped in an old sleeve.")
      pbMessage("Seller: Keep the cloth. Better round a bottle than forgotten in a drawer.")
      pbMessage("Seller: Still the same little face. Every year I need stronger spectacles.")
    end

    def journal
      choices = ["Read today's page", "Write your name", "Close the book"]
      case pbMessage("A notebook lies open beside the shelf.", choices, -1)
      when 0
        text =
          if Tidebound.story[:dream_room] &&
               %i[sealed wick folded].include?(Tidebound.story[:dream_room][:phase])
            "The room has not finished with you."
          elsif Tidebound.story[:psychic_maze] == :active
            "Find Wick. Arrows slide, diamonds stop, and circles jump."
          elsif !Tidebound.story[:bedroom_talk]
            "Play with Wick in your room."
          elsif !Tidebound.story[:hall_talk]
            "Mother wants to talk in the main hall."
          elsif Tidebound.story[:walk_state] == :at_pier
            "Pookie is at the end of the pier. Speak to her and bring her home."
          elsif Tidebound.story[:walk_state] == :following
            "Walk Pookie around the village, then go home together: #{Tidebound.story[:walk_steps]}/100 steps."
          elsif Tidebound.story[:walk_state] != :complete
            "Pookie is sleeping outside, beside the lighthouse. Take her for a walk."
          elsif !Tidebound.story[:starter_chosen]
            "Speak to Mother, then choose one of our three household companions."
          elsif !Tidebound.story[:oil_requested]
            "Speak to Mother before setting out."
          elsif !Tidebound.story[:shop_unlocked] && $bag.has?(:TIDEBOUNDOILKEYS)
            "Return the oil-shop keys to the seller outside his shop."
          elsif Tidebound.story[:keys_requested] && !Tidebound.story[:shop_unlocked]
            "Look for the seller's keys among the white flowers in the northern wood."
          elsif !Tidebound.story[:shop_unlocked]
            "Ask the seller outside the oil shop for Mother's bottle."
          elsif !Tidebound.story[:oil_collected]
            "The oil shop is open. Go inside for Mother's bottle."
          elsif !Tidebound.story[:oil_returned]
            "Bring the oil home."
          elsif !Tidebound.story[:lamp_lit]
            "Tend the great lamp upstairs, just as Mother showed you."
          elsif Tidebound::Interactions.hint
            Tidebound::Interactions.hint
          elsif !Tidebound.story[:fire_found]
            "A traveller has lit a fire in the forest."
          else
            "The northern road has fallen. The traveller will wait beside his fire."
          end
        pbMessage(text)
      when 1
        name = pbEnterPlayerName("Your name?", 1, 10, $player.name)
        $player.name = name unless name.empty?
      end
    end

    def forest_gate
      unless Tidebound.story[:starter_chosen]
        pbMessage(
          "The northern path is disappearing into mist. There is something to finish at home first."
        )
        $game_player.moveto(*Tidebound::World.coast_xy(24, 4))
        $game_player.turn_down
        return
      end
      Tidebound::World.travel(:forest, 17, 25, 8)
    end

    def pier
      if %i[following at_pier running].include?(Tidebound.story[:walk_state])
        pbMessage("You look where Pookie was looking. There is only dark water.")
        return
      end
      return if Tidebound.story[:pier_seen] && !Tidebound.story[:oil_returned]
      if !Tidebound.story[:oil_returned]
        Tidebound.story[:pier_seen] = true
        pbMessage("An empty berth. The rope still pulls against its knot.")
      elsif !Tidebound.story[:lapras_glimpsed]
        Tidebound::SeaGlimpse.play
      else
        pbMessage("You wait until the end of a wave. Nothing surfaces.")
      end
    ensure
      self.lapras_visible = false
    end

    def fire
      unless Tidebound.story[:fire_found]
        Tidebound.story[:fire_found] = true
        pbMessage("Traveller: Come closer. There is room.")
        pbMessage(
          "Traveller: The northern bridge is gone. I was meant to meet someone on the other side."
        )
        pbMessage("Traveller: I'll keep the fire burning. You can wait with me.")
      end
      choice =
        pbMessage(
          "A little warmth reaches your hands.",
          ["Rest", "Ask about the wood", "Leave"],
          -1
        )
      if choice == 0
        Tidebound::FieldDetails.rest(:wood_fire, [103, 11, 22, 8])
      elsif choice == 1
        pbMessage("Traveller: The birds have come back. They won't go near the pool, though.")
        pbMessage(
          "Traveller: Something there wears a drowned man's sleeves. Leave it be if you're tired."
        )
      end
    end

    def bird
      return if Tidebound.story[:wood_bird_gone]
      return unless pbConfirmMessage("A Natu watches you from the roots. Approach it?")
      result = Tidebound::Encounters.fight(:NATU, 4)
      Tidebound.story[:wood_bird_gone] = true if [1, 4].include?(result)
    end

    def pool
      if Tidebound.story[:pool_cleared]
        pbMessage("The pool is still. Nothing in it reflects the trees.")
        return
      end
      pbMessage("A pale shape lifts its arms beneath the surface.")
      unless pbConfirmMessage(
               "It turns towards you and your companion. Face the thing in the water?"
             )
        return
      end
      foe = Pokemon.new(:FRILLISH, 12)
      foe.moves.clear
      %i[WATERGUN NIGHTSHADE ABSORB].each { |m| foe.learn_move(m) }
      result = Tidebound::Encounters.fight(foe)
      if [1, 4].include?(result)
        Tidebound.story[:pool_cleared] = true
        pbMessage("The branches stop trembling.")
      end
    end

    def northern_way
      pbMessage("Beyond the last trees, the bridge has fallen into the gorge.")
      pbMessage("You can still see a lantern burning on the other side.")
      unless Tidebound.story[:chapter_end]
        Tidebound.story[:chapter_end] = true
        pbMessage(
          "The first chapter ends here. You can keep exploring the village and the wood, and save from the menu."
        )
      end
      $game_player.moveto(17, 4)
      $game_player.turn_down
    end
  end
end
