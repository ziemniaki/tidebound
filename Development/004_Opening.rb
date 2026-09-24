# Tidebound opening, Essentials 21.1. These scripts are embedded before Main.
module Tidebound
  module Opening
    DAYLIGHT_MAPS = [].freeze # Only explicitly approved magical locations.
    NIGHT_TONE = [-80, -74, -48, 150].freeze
    MAP_IDS = [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116].freeze
    HOUSE_PETS = {
      :NATU => ["Wick", [:PECK, :LEER, :NIGHTSHADE]],
      :MAKUHITA => ["Maku", [:TACKLE, :ARMTHRUST, :SANDATTACK, :FORESIGHT]],
      :POOCHYENA => ["Pookie", [:TACKLE, :HOWL, :SANDATTACK, :BITE]]
    }.freeze
    class << self
      attr_accessor :lapras_visible
    end
    module_function

    def flags
      Tidebound.state.story
    end

    # Migrate by story revision, never by party size: an empty party may be grief.
    def migrate_opening!
      return unless flags[:opening_started]
      revision = flags[:opening_revision]
      return if revision && revision >= 4
      unless revision
        flags[:legacy_companion] = true
        flags[:starter_chosen] = true
        flags[:lamp_lit] = true if flags[:oil_returned]
      end
      # Existing journeys keep all companions, losses and errand progress.
      # The new childhood scene is for new games; never reset an old save.
      flags[:opening_revision] = 4
      flags[:bedroom_talk] = true
      flags[:hall_talk] = true
      flags[:walk_state] = :complete
      flags[:walk_steps] = 100
      flags[:shop_unlocked] = true
    end

    def household_pets
      flags[:household_pets] ||= {}
    end

    def erase_autorun
      pbMapInterpreter&.get_self&.erase
    end

    def travel(map_id, x, y, direction = 2)
      pbFadeOutIn do
        $game_temp.player_new_map_id = map_id
        $game_temp.player_new_x = x
        $game_temp.player_new_y = y
        $game_temp.player_new_direction = direction
        $scene.transfer_player
        $game_map.refresh
      end
    end

    def begin_story
      erase_autorun
      migrate_opening!
      return if flags[:opening_started]
      flags[:opening_started] = true
      flags[:psychic_maze] = :active if $game_map.map_id == 114
      flags[:dream_room] = {phase: :sealed, streak: 0} if $game_map.map_id == 115
      flags[:coast_revision] = 5
      flags[:opening_revision] = 4
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
      flags[:walk_state] = :not_started
      flags[:walk_steps] = 0
      if $game_map.map_id == 115
        pbMessage("A room. Your room, probably.")
      elsif flags[:psychic_maze] == :active
        pbMessage("You tap twice against the blanket. Somewhere beyond the shelves, Wick taps back.")
        pbMessage("One more game. Find Wick.")
      else
        pbMessage("Wick hops across your blanket. You tap twice; he taps back.")
        pbMessage("Outside, the lamp turns. In here, it is still your little world.")
        pbMessage("Wick is waiting for your next move. Speak to him with the action button.")
      end
    end

    def mother
      migrate_opening!
      unless flags[:hall_talk]
        hall_talk
        return
      end
      unless flags[:walk_state] == :complete
        if flags[:walk_state] == :at_pier
          pbMessage("Mother: Where is Pookie, love? Don't leave her out there alone.")
        elsif flags[:walk_state] == :following && flags[:walk_steps].to_i >= 100
          finish_walk
        elsif flags[:walk_state] == :following
          pbMessage("Mother: A little longer, love. She has been waiting all morning.")
          pbMessage("Pookie's walk: #{flags[:walk_steps]}/100 steps outside.")
        else
          pbMessage("Mother: Pookie is asleep beside the lighthouse. Take her for a little walk around the village.")
        end
        return
      end
      unless flags[:starter_chosen]
        flags[:choice_explained] = true
        pbMessage("Mother: It isn't safe to travel alone. One of our little family should go with you.")
        pbMessage("Mother: Wick, Maku, or Pookie. Ask whichever one you want beside you. The others will keep me company.")
        return
      end
      if !flags[:oil_requested]
        flags[:oil_requested] = true
        pbMessage("Mother: Before you go far, will you fetch the lamp oil? The little shop beyond the tower keeps a bottle for us.")
        pbMessage("Mother: There are things I want to teach you while I still can. The light is one of them.")
      elsif flags[:oil_collected] && !flags[:oil_returned]
        flags[:oil_returned] = true
        pbMessage("She takes the bottle in both hands. For a moment, neither of you lets go.")
        pbMessage("Mother: Thank you. Come, you should know how to tend it yourself.")
        pbMessage("She shows you the measure on the bottle and how to trim the wick.")
        if flags[:legacy_companion]
          flags[:lamp_lit] = true
          pbMessage("Mother: That should last until morning. Mind your footing in the wood.")
        else
          pbMessage("Mother: Take it upstairs to the great lamp. Only that one, please.")
        end
      elsif flags[:oil_returned] && !flags[:lamp_lit]
        pbMessage("Mother: The great lamp, upstairs. Pour to the line, then turn the brass wheel.")
      elsif flags[:lamp_lit]
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
      if flags[:lamp_lit]
        pbMessage("The great lamp turns.\nFor a moment, the sea has an edge.")
      elsif !flags[:oil_returned]
        pbMessage("The flame has grown thin. Mother will know what it needs.")
      else
        pbMessage("You pour to the line, trim the wick and turn the brass wheel.")
        flags[:lamp_lit] = true
        pbMessage("The flame steadies. Beyond the glass, a strip of water becomes silver.")
        pbMessage("Mother calls from below: That's it, love. Now you know how to bring the light back.")
      end
    end

    def house_pet(species)
      pet = household_pets[species]
      return unless pet
      description = {
        :NATU => "Wick tilts his head before you speak, as though he remembers the question.",
        :MAKUHITA => "Maku leans against your knee. He has always carried the heavy things for Mother.",
        :POOCHYENA => "Pookie presses her nose into your palm. She will not look at the sea-facing window."
      }
      pbMessage(description[species])
      return if flags[:starter_chosen]
      unless flags[:walk_state] == :complete
        pbMessage("For now, there is a little walk to take together.")
        return
      end
      mother unless flags[:choice_explained]
      flags[:choice_explained] = true
      return unless pbConfirmMessage("Ask #{pet.name}, the #{pet.speciesName}, to come with you?")
      # Keep this individual, including identity and stats, rather than rolling a new one.
      pet.owner = Pokemon::Owner.new_from_trainer($player)
      $player.party << pet
      household_pets.delete(species)
      flags[:starter_chosen] = species
      $bag.add(:POKEBALL, 8)
      pbMessage("#{pet.name} settles beside you. This time, you are going together.")
      pbMessage("Mother gives you eight Poké Balls, wrapped in a clean handkerchief.")
      mother
    end

    def oil_seller
      unless $game_map.map_id == 106 && flags[:shop_unlocked]
        pbMessage("The bottle is inside the locked shop.")
        return
      end
      unless flags[:oil_requested]
        pbMessage("Seller: Your mother has been keeping late hours. Go and see her, will you?")
        return
      end
      if flags[:oil_collected]
        pbMessage("Seller: I used to sell enough oil to keep three boats going.")
        pbMessage("Seller: The empty bottles make a lovely sound when the wind gets in.")
        return
      end
      flags[:oil_collected] = true
      pbMessage("Seller: The keeper's bottle. Already paid for.")
      pbMessage("You take the lamp oil. The glass is wrapped in an old sleeve.")
      pbMessage("Seller: Keep the cloth. Better round a bottle than forgotten in a drawer.")
      pbMessage("Seller: Still the same little face. Every year I need stronger spectacles.")
    end

    def journal
      choices = ["Read today's page", "Write your name", "Close the book"]
      case pbMessage("A notebook lies open beside the shelf.", choices, -1)
      when 0
        text = if flags[:dream_room] && [:sealed,:wick,:folded].include?(flags[:dream_room][:phase])
                 "The room has not finished with you."
               elsif flags[:psychic_maze] == :active
                 "Find Wick. Arrows slide, diamonds stop, and circles jump."
               elsif !flags[:bedroom_talk]
                 "Play with Wick in your room."
               elsif !flags[:hall_talk]
                 "Mother wants to talk in the main hall."
               elsif flags[:walk_state] == :at_pier
                 "Pookie is at the end of the pier. Speak to her and bring her home."
               elsif flags[:walk_state] == :following
                 "Walk Pookie around the village, then go home together: #{flags[:walk_steps]}/100 steps."
               elsif flags[:walk_state] != :complete
                 "Pookie is sleeping outside, beside the lighthouse. Take her for a walk."
               elsif !flags[:starter_chosen]
                 "Speak to Mother, then choose one of our three household companions."
               elsif !flags[:oil_requested]
                 "Speak to Mother before setting out."
               elsif !flags[:shop_unlocked] && $bag.has?(:TIDEBOUNDOILKEYS)
                 "Return the oil-shop keys to the seller outside his shop."
               elsif flags[:keys_requested] && !flags[:shop_unlocked]
                 "Look for the seller's keys among the white flowers in the northern wood."
               elsif !flags[:shop_unlocked]
                 "Ask the seller outside the oil shop for Mother's bottle."
               elsif !flags[:oil_collected]
                 "The oil shop is open. Go inside for Mother's bottle."
               elsif !flags[:oil_returned]
                 "Bring the oil home."
               elsif !flags[:lamp_lit]
                 "Tend the great lamp upstairs, just as Mother showed you."
               elsif defined?(Tidebound::NeighborQuest) && Tidebound::NeighborQuest.hint
                 Tidebound::NeighborQuest.hint
               elsif !flags[:fire_found]
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
      unless flags[:starter_chosen]
        pbMessage("The northern path is disappearing into mist. There is something to finish at home first.")
        $game_player.moveto(*coast_xy(24, 4))
        $game_player.turn_down
        return
      end
      travel(103, 17, 25, 8)
    end

    def pier
      if [:following, :at_pier, :running].include?(flags[:walk_state])
        pbMessage("You look where Pookie was looking. There is only dark water.")
        return
      end
      return if flags[:pier_seen] && !flags[:oil_returned]
      if !flags[:oil_returned]
        flags[:pier_seen] = true
        pbMessage("An empty berth. The rope still pulls against its knot.")
      elsif !flags[:lapras_glimpsed]
        lapras_scene
      else
        pbMessage("You wait until the end of a wave. Nothing surfaces.")
      end
    ensure
      self.lapras_visible = false
    end

    def fire
      unless flags[:fire_found]
        flags[:fire_found] = true
        pbMessage("Traveller: Come closer. There is room.")
        pbMessage("Traveller: The northern bridge is gone. I was meant to meet someone on the other side.")
        pbMessage("Traveller: I'll keep the fire burning. You can wait with me.")
      end
      choice = pbMessage("A little warmth reaches your hands.", ["Rest", "Ask about the wood", "Leave"], -1)
      if choice == 0
        Tidebound::FieldDetails.rest(:wood_fire, [103, 11, 22, 8])
      elsif choice == 1
        pbMessage("Traveller: The birds have come back. They won't go near the pool, though.")
        pbMessage("Traveller: Something there wears a drowned man's sleeves. Leave it be if you're tired.")
      end
    end

    def fight(*foes)
      result = Tidebound.wild!(*foes)
      if result == :astral
        pbMessage("The sound of the world draws away.")
        travel(105, 15, 21, 8)
      end
      result
    end

    def bird
      return if flags[:wood_bird_gone]
      return unless pbConfirmMessage("A Natu watches you from the roots. Approach it?")
      result = fight(:NATU, 4)
      flags[:wood_bird_gone] = true if [1, 4].include?(result)
    end

    def pool
      if flags[:pool_cleared]
        pbMessage("The pool is still. Nothing in it reflects the trees.")
        return
      end
      pbMessage("A pale shape lifts its arms beneath the surface.")
      return unless pbConfirmMessage("It turns towards you and your companion. Face the thing in the water?")
      foe = Pokemon.new(:FRILLISH, 12)
      foe.moves.clear
      [:WATERGUN, :NIGHTSHADE, :ABSORB].each { |m| foe.learn_move(m) }
      result = fight(foe)
      if [1, 4].include?(result)
        flags[:pool_cleared] = true
        pbMessage("The branches stop trembling.")
      end
    end

    def northern_way
      pbMessage("Beyond the last trees, the bridge has fallen into the gorge.")
      pbMessage("You can still see a lantern burning on the other side.")
      unless flags[:chapter_end]
        flags[:chapter_end] = true
        pbMessage("The first chapter ends here. You can keep exploring the village and the wood, and save from the menu.")
      end
      $game_player.moveto(17, 4)
      $game_player.turn_down
    end

    def astral_arrival
      erase_autorun
      return unless Tidebound.state.realm == :astral
      # The arrival message runs once per journey, including after save/reload.
      unless flags[:astral_arrival_journey] == Tidebound.state.journey
        flags[:astral_arrival_journey] = Tidebound.state.journey
      pbMessage("No wind. No footsteps.\nNo familiar weight beside you.")
        pbMessage("Somewhere in the fog, a familiar cry answers itself.")
      end
      give_guide
    end

    def give_guide
      Tidebound.borrow_guide! if $player.able_pokemon_count == 0
      unless flags[:astral_balls_journey] == Tidebound.state.journey
        flags[:astral_balls_journey] = Tidebound.state.journey
        $bag.add(:POKEBALL, 18)
      end
    end

    def guide
      give_guide
      pbMessage("Traveller: You can hear them. That is something.")
      pbMessage("Traveller: This bird will keep you company here. It cannot cross with you.")
      pbMessage("Find your companions in the fog. Each allows one encounter: catch them before six turns pass. If they faint, you flee, or time runs out, they are lost.")
      pbMessage("Traveller: The way back is behind me. Leave no one you still mean to find.")
    end

    def spirit(index)
      record = Tidebound.state.souls[index]
      return unless record && record.status == :waiting
      give_guide
      pbMessage("#{record.pokemon.name} turns at the sound of your voice.")
      return unless pbConfirmMessage("Reach for #{record.pokemon.name}? There is one encounter, with six turns to catch them. Failure is permanent.")
      result = Tidebound.recover_spirit!(record.id)
      if result == :recovered
        pbMessage("A familiar weight settles against you.\n#{record.pokemon.name} has returned, weak but real.")
      else
        pbMessage("For an instant, #{record.pokemon.name} seems to recognize you.")
        pbMessage("Then the shape is gone.")
      end
    end

    def return_from_astral
      return unless Tidebound.state.realm == :astral
      remaining = Tidebound.state.waiting_ids.length
      prompt = if remaining > 0
                 "#{remaining} #{remaining == 1 ? 'companion still waits' : 'companions still wait'} in the fog. Leaving will lose them permanently. Return to the living shore?"
               else
                 "The shore is very far away. Return to it?"
               end
      unless pbConfirmMessageSerious(prompt)
        $game_player.moveto(15, 21)
        $game_player.turn_up
        return
      end
      no_survivors = $player.party.none? { |p| !Tidebound.borrowed?(p) }
      point = Tidebound.return_to_living!
      travel(*point)
      if no_survivors
        pbMessage("A small Natu waits beside you. It is not the bird you lost.")
      else
        pbMessage("Cold air. The weight of your own body.\nSomeone has kept a place for you.")
      end
    end

    def memorial
      lost = Tidebound.state.memorials
      if lost.empty?
        pbMessage("There are small hollows in the stone.\nNone yet carries a name.")
      else
        labels = lost.map { |s| "#{s.pokemon.name} - #{s.pokemon.speciesName}" }
        choice = pbMessage("The stone remembers.", labels + ["Step away"], -1)
        if choice >= 0 && choice < lost.length
          pkmn = lost[choice].pokemon
          pbMessage("#{pkmn.name}.\nLevel #{pkmn.level}.\nThere was a time when this name brought them running.")
        end
      end
    end

    def perpetual_night?
      $game_map && MAP_IDS.include?($game_map.map_id) && !DAYLIGHT_MAPS.include?($game_map.map_id)
    end

    def atmosphere
      migrate_coast!
      return unless MAP_IDS.include?($game_map.map_id)
      astral = $game_map.map_id == 105
      migrate_opening!
      indoor = [101, 104, 106, 107, 109, 110, 111, 113, 114, 115, 116].include?($game_map.map_id)
      tone = if $game_map.map_id == 116
               Tone.new(-20, -30, -12, 25)
             elsif [110,111].include?($game_map.map_id)
               Tone.new(-38, -38, -30, 65)
             elsif indoor
               Tone.new(-8, -14, -25, 12)
             elsif DAYLIGHT_MAPS.include?($game_map.map_id)
               Tone.new(0, 0, 0, 0)
             elsif astral
               Tone.new(-55, -46, -20, 160)
             else
               Tone.new(*NIGHT_TONE)
             end
      $game_screen.start_tone_change(tone, 0)
      $game_map.fog_name = indoor ? "" : "smoke"
      $game_map.fog_opacity = indoor ? 0 : (astral ? 95 : 24)
      $game_map.fog_zoom = 160
      $game_map.fog_sx = astral ? -2 : 1
      $game_map.fog_sy = 0
      $game_map.fog_blend_type = 0
    end
  end
end

# Passage masks belong only to the opening maps. Character collision,
# touch/action events and map bounds remain the engine's normal implementations.
module Tidebound::OpeningPassages
  def passable?(x, y, d, self_event = nil)
    mask = Tidebound::MAP_PASSAGES[@map_id]
    return super unless mask
    return valid?(x, y) && mask[y][x] == "1"
  end
  def playerPassable?(x, y, d, self_event = nil)
    return passable?(x, y, d, self_event) if Tidebound::MAP_PASSAGES[@map_id]
    super
  end
  def passableStrict?(x, y, d, self_event = nil)
    return passable?(x, y, d, self_event) if Tidebound::MAP_PASSAGES[@map_id]
    super
  end
  def terrain_tag(x, y, count_bridge = false)
    return GameData::TerrainTag.get(:None) if Tidebound::MAP_PASSAGES[@map_id]
    super
  end
end
Game_Map.prepend(Tidebound::OpeningPassages)

EventHandlers.add(:on_enter_map, :tidebound_atmosphere, proc { |_old_map_id| Tidebound::Opening.atmosphere })
# Loading a save does not always enter a new map.
EventHandlers.add(:on_new_spriteset_map, :tidebound_restore_tone, proc { |_spriteset, _viewport| Tidebound::Opening.atmosphere })


# Ordinary story locations stay night regardless of host time. Real timers still run.
module TideboundNightClock
  def isNight?(time = nil)
    return true if Tidebound::Opening.perpetual_night?
    super
  end
  [:isDay?, :isMorning?, :isAfternoon?, :isEvening?].each do |name|
    define_method(name) do |time = nil|
      next false if Tidebound::Opening.perpetual_night?
      super(time)
    end
  end
  def getShade
    return 0 if Tidebound::Opening.perpetual_night?
    super
  end
end
PBDayNight.singleton_class.prepend(TideboundNightClock) if defined?(PBDayNight)
module TideboundNightBattle
  def prepare_battle(battle)
    super
    battle.time = 2 if Tidebound::Opening.perpetual_night?
  end
end
if defined?(BattleCreationHelperMethods)
  BattleCreationHelperMethods.singleton_class.prepend(TideboundNightBattle)
end
