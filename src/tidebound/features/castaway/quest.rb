module Tidebound::Castaway
  PASS_ORDER = [1, 0, 2].freeze
  module_function

  def flags
    Tidebound.story[:castaway] ||= {}
  end

  def say(*lines)
    lines.each { |line| pbMessage(line) }
  end

  def refresh
    Tidebound::Actors.refresh($game_map)
  end

  # The shipboard chapter and the smaller Psyduck Island stop will fit before
  # this crossing. For now the missed destination is acknowledged on arrival.
  def depart
    return unless Tidebound::Encounters.able?
    returning = !!flags[:completed]
    prompt =
      returning ? "Sail back to the sunny island?" : "Board the Little Promise for Psyduck Island?"
    return unless pbConfirmMessage(prompt)
    Tidebound::CastawayVoyage.play(returning: false)
    Tidebound::World.travel(:wreck_beach, :arrival)
    Tidebound.state.checkpoint = [Tidebound::World::MAPS.fetch(:wreck_beach), 15, 18, 2]
    Tidebound::DemoLaunch.flags[:completed] = true
  end

  def arrival
    Tidebound::World.erase_autorun
    return if flags[:greeted]
    flags[:arrived] = true
    Tidebound.state.checkpoint = [Tidebound::World::MAPS.fetch(:wreck_beach), 15, 18, 2]
    say(
      "Warm sand. Your shadow lies sharp and small beside you.",
      "Your companions are here. Your bag is dry inside its waxed cover.",
      "Captain: All three of us ashore. That's what matters. Nell's over by the sail.",
      "Captain: The current carried us past Psyduck Island. This reef wasn't on my chart.",
      "Captain: I've forgotten how to stand in this much light.",
      "Captain: The hull can be mended. First we need fresh water and a patch of shade."
    )
    flags[:greeted] = true
  end

  def captain
    if flags[:completed]
      say("Captain: She still knows the way home. So do we, now.")
      return_home
    elsif flags[:signalled]
      say(
        "Captain: A fishing cutter answered your signal. They'll guide us through the reef.",
        "Captain: We can leave when you're ready. Nothing here needs to be left behind."
      )
      return_home
    elsif flags[:repaired]
      say(
        "Captain: The hull is sound. We need someone who knows this reef.",
        "Captain: Take the spare sail up to the ridge. A pale square against the trees will carry a long way."
      )
    elsif flags[:water] && flags[:shelter] && flags[:tools]
      say(
        "Captain: Clean water, shade and the shipwright's kit. That's a beginning.",
        "You hold the boards steady while the captain fits the new pegs. Nell works the seams.",
        "Captain: She'll float again. Now we need a safe passage through that reef."
      )
      flags[:repaired] = true
      refresh
    else
      tasks = []
      tasks << "Find fresh water inland." unless flags[:water]
      unless flags[:shelter]
        tasks << "Recover the sailcloth on the eastern beach and ask Nell to rig some shade."
      end
      unless flags[:tools]
        tasks << "Find the shipwright's kit. Its red chest washed around the headland."
      end
      say("Captain: #{tasks.join(" ")}", "Captain: I'll stay with the hull. One board at a time.")
    end
  end

  def nell
    if flags[:canvas] && !flags[:shelter]
      say(
        "Nell: There. Between those two spars. Help me with the corner?",
        "The canvas lifts. A rectangle of cool shade settles over the sand.",
        "Nell: Almost a room. I'll keep our stores and resting companions here."
      )
      flags[:shelter] = true
      refresh
    else
      say(
        (
          if flags[:shelter]
            "Nell: I keep thinking I ought to turn a lamp on. Then I look up."
          else
            "Nell: There's dry sailcloth farther east. We could make a little shade."
          end
        )
      )
    end
    choice =
      pbMessage(
        "Nell: What do you need?",
        ["Resting companions", "Camp supplies", "Talk", "Leave"],
        -1
      )
    case choice
    when 0
      Tidebound::Sanctuary.open
    when 1
      supplies
    when 2
      say(
        "Nell: The letters stayed dry. Wax around the lid. Old habit.",
        "Nell: I counted them before I counted the flour. Don't tell the captain."
      )
    end
  end

  def supplies
    if flags[:supplies]
      return(
        say("Nell: I've already put your share with your things. The fruit still grows, though.")
      )
    end
    say("Nell: Some catching balls and medicine survived in the dry chest. Take them.")
    # Deliver each stack once. A full pocket can retry without duplicating the other.
    unless flags[:balls]
      return unless pbReceiveItem(:GREATBALL, 12)
      flags[:balls] = true
    end
    unless flags[:medicine]
      return unless pbReceiveItem(:SUPERPOTION, 5)
      flags[:medicine] = true
    end
    flags[:supplies] = true
  end

  def salvage(kind)
    if flags[kind]
      return(
        say(
          (
            if kind == :canvas
              "Only a few threads cling to the driftwood."
            else
              "The red chest is empty. Its tools are back at camp."
            end
          )
        )
      )
    end
    unless pbConfirmMessage(
             (
               if kind == :canvas
                 "A dry fold of sailcloth is caught above the tide. Carry it back?"
               else
                 "The shipwright's red chest rests among the roots. Carry the kit back to camp?"
               end
             )
           )
      return
    end
    flags[kind] = true
    say(
      (
        if kind == :canvas
          "You recover enough canvas for shade, with a broad strip to spare."
        else
          "Wooden pegs, a small mallet, caulking and a hand drill. Everything smells of the ship."
        end
      )
    )
    refresh
  end

  def spring
    if flags[:water]
      return(
        say(
          "Clear water slips along the old channel. Below, something splashes in a shallow stone bowl."
        )
      )
    end
    say(
      "Fresh water seeps from the rock, then disappears beneath fallen leaves.",
      "One groove runs towards salt-stained sand. Another ends in exposed roots. A stone-lined channel leads to a dry collecting bowl."
    )
    choice =
      pbMessage(
        "Which channel will you clear?",
        [
          "The salt-stained groove",
          "The groove among the roots",
          "The stone-lined channel",
          "Leave"
        ],
        -1
      )
    if choice == 2
      say(
        "You lift the leaves and ease out a fallen branch. Water gathers in the bowl, then spills into the grove.",
        "From the trees comes a brief chorus of calls. You fill the ship's water flask."
      )
      flags[:water] = true
      refresh
    elsif choice >= 0 && choice < 2
      say("The water soaks away. The collecting bowl remains dry. You can try another channel.")
    end
  end

  def fruit
    unless flags[:fruit]
      say("Ripe fruit lies in an open husk. You keep one sound piece for the troop.")
      flags[:fruit] = true
    else
      Tidebound::FieldDetails.berry($game_map.map_id, 10, 12, :ORANBERRY)
    end
  end

  def troop
    if flags[:troop]
      return(
        say(
          "A Passimian catches your eye, then passes a fruit along the branch. The path stays open."
        )
      )
    end
    unless flags[:water]
      return(
        say(
          "The troop gathers around a dry bowl. One carries an empty fruit husk towards the sound of the spring.",
          "A broad-shouldered Passimian holds its ground across the eastern path."
        )
      )
    end
    say(
      "The bowl is full. The troop drinks, then begins a passing game.",
      "A youngster at the forked trunk throws to the low branch. The last receiver waits on a flat stone."
    )
    unless flags[:fruit]
      say("There is ripe fruit in the grove. Perhaps you could join in.")
      return
    end
    return unless pbConfirmMessage("Join their passing game with your fruit?")
    PASS_ORDER.each do |expected|
      choice =
        pbMessage(
          "Where will you pass the fruit?",
          ["The low branch", "The forked trunk", "The flat stone", "Step back"],
          -1
        )
      return if choice < 0 || choice >= 3
      unless choice == expected
        return(
          say("A hand catches the fruit and rolls it back to you. Watch their order and try again.")
        )
      end
      say("A quick catch. An expectant call from farther along the line.")
    end
    say(
      "The last Passimian places your fruit with the others. The troop makes room along the path."
    )
    flags[:troop] = true
    refresh
  end

  def garden_path
    unless flags[:troop]
      return(
        say(
          "The troop still guards this path. They keep looking towards the dry bowl and the fruit grove."
        )
      )
    end
    Tidebound::World.travel(:island_garden, :canopy)
  end

  def journal
    say(
      "A slate lies beneath the roots. Rain has spared a few lines.",
      "'Cleared the channel. The little ones came back before the water did.'",
      "'Leave the first fruit on the flat stone. They know whose tree it is.'",
      "Below that, a child's hand has scratched a very tall tree. There is no name."
    )
    flags[:journal] = true
  end

  def signal
    if flags[:signalled]
      return(
        say(
          "The pale sail turns in the wind. Beyond the reef, a small boat answers with a flash.",
          "The captain is waiting at Wreck Beach."
        )
      )
    end
    unless flags[:repaired]
      return(
        say(
          "From here, a square of pale cloth would be visible beyond the reef.",
          "The captain must finish repairing the hull before anyone can guide it out."
        )
      )
    end
    return unless pbConfirmMessage("Raise the spare sail on the old signal frame?")
    say("You haul the canvas up. For a long while there is only the wind.")
    flags[:signalled] = true
    refresh
    pbWait(1.5)
    say("Then, beyond the reef: a small answering flash.", "Someone has seen you.")
  end

  def return_home
    unless pbConfirmMessage("Sail home? You can return to the island with the captain later.")
      return
    end
    return unless flags[:signalled] || flags[:completed]
    Tidebound::CastawayVoyage.play(returning: true)
    Tidebound::World.travel(:docks, :captain)
    flags[:completed] = true
    Tidebound.state.checkpoint = [
      Tidebound::World::MAPS.fetch(:docks),
      *Tidebound::World::ENTRANCES.fetch(Tidebound::World::MAPS.fetch(:docks)).fetch("captain")
    ]
    say(
      "The harbour lamps are small and steady. You remember what the sand felt like when it was warm."
    )
  end

  def rest
    Tidebound::FieldDetails.rest(:castaway, [Tidebound::World::MAPS.fetch(:wreck_beach), 15, 18, 2])
  end

  def wildlife(species, level, text)
    say(text)
    return unless pbConfirmMessage("Approach for a wild encounter?")
    return unless Tidebound::Encounters.able?
    pokemon = Pokemon.new(species, level)
    pokemon.form = Tidebound::WILD_FORMS.dig($game_map.map_id, pokemon.species.to_s) || 0
    pokemon.reset_moves
    Tidebound::Encounters.fight(pokemon)
  end
end
