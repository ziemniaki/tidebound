# Small, optional harbour stories. State is additive; rewards remain retryable.
module Tidebound::Harbour
  LETTER = :TIDEBOUNDLETTER
  SHUTTLE = :TIDEBOUNDSHUTTLE
  module_function

  def flags
    Tidebound.story[:harbour] ||= {}
  end

  def say(*lines)
    lines.each { |line| pbMessage(line) }
  end

  def reward(key, item, count = 1)
    return true if flags[key]
    unless pbReceiveItem(item, count)
      say("Make a little room in your bag. I will keep it for you.")
      return false
    end
    flags[key] = true
    true
  end

  def courier
    if flags[:letter_delivered]
      say(
        "Jory: She read it? Good. Her daughter pays for the reply before she writes her own letter."
      )
      reward(:letter_paid, :ORANBERRY, 2)
      return
    end
    if $bag.has?(LETTER)
      return(
        say(
          "Jory: Irena is by the lamp north-west of the museum. The envelope stays sealed, please."
        )
      )
    end
    say(
      "Jory: I used to carry passengers. Now I carry what they cannot say to each other.",
      "Jory: There is a letter for Irena, by the lamp north-west of the museum. My watch starts before I can take it."
    )
    return unless pbConfirmMessage("Deliver the sealed letter?")
    if pbReceiveItem(LETTER)
      flags[:letter_started] = true
      say("Jory: Thank you. It is from her daughter. She is alive. I always say that first.")
    end
  end

  def resident
    if flags[:letter_delivered]
      return(
        say(
          "Irena: She says there is a room. With a window that opens.",
          "Irena: I have started deciding what I can carry. That is different from deciding to go."
        )
      )
    end
    unless $bag.has?(LETTER)
      return(
        say(
          "Irena: I made rope here for thirty years. My hands still twist the bedsheet in my sleep.",
          "Irena: My daughter writes from inland. I keep meaning to ask Jory if another letter has come."
        )
      )
    end
    say("Irena takes the sealed letter. She reads the address twice before opening it.")
    $bag.remove(LETTER)
    flags[:letter_delivered] = true
    say(
      "Irena: She has painted the little room. She says I would like the colour.",
      "Irena: Tell Jory it arrived. Do not tell him I cried. He will try to charge for the water."
    )
  end

  def mender
    if flags[:shuttle_returned]
      say(
        "Sella: My brother mended this scarf until there was more mend than scarf. It still does its work."
      )
      reward(:shuttle_paid, :SILKSCARF)
      return
    end
    if $bag.has?(SHUTTLE)
      $bag.remove(SHUTTLE)
      flags[:shuttle_returned] = true
      say(
        "Sella turns the wooden shuttle over. Three little cuts mark its handle.",
        "Sella: My brother's. He lost two fingers to a winch, then taught himself all over again.",
        "Sella: People at the ring call that sort of thing a good story. He mostly called it inconvenient."
      )
      reward(:shuttle_paid, :SILKSCARF)
      return
    end
    say(
      "Sella: A net is mostly holes held in the right places. This one has ambitions.",
      "Sella: I left my netting shuttle in the folded nets beside the western pier. Find it before the tide does?"
    )
    flags[:shuttle_started] = true if pbConfirmMessage("Look for Sella's shuttle?")
  end

  def nets
    if flags[:shuttle_returned] || $bag.has?(SHUTTLE)
      return say("The folded nets smell of salt and old rain. The little hollow is empty.")
    end
    unless flags[:shuttle_started]
      return(
        say(
          "A wooden netting shuttle lies deep in a folded net. Someone has kept its handle smooth."
        )
      )
    end
    say(
      "You work the shuttle free without cutting the net. Three marks are carved into its handle."
    )
    pbReceiveItem(SHUTTLE)
  end

  CARGO = {
    west: "WEST LOT: five sacks of flour; two sealed tins of lamp oil.",
    middle: "MIDDLE LOT: four sacks of flour; two sealed tins of lamp oil.",
    east:
      "EAST LOT: three sacks of flour; one sealed tin of lamp oil. A clean circle marks an empty space."
  }.freeze

  def cargo(id)
    say(CARGO.fetch(id))
    (flags[:counted] ||= {})[id] = true
    say("A note now records the returned sixth tin.") if id == :east && flags[:oil_returned]
  end

  def porter
    if flags[:oil_returned]
      say(
        "Daro: Six tins. A village can light its windows and Harker can find his own oil.",
        "Daro: I used to lift all this. Now I count it. Turns out that matters too."
      )
      reward(:cargo_paid, :ORANBERRY, 3)
      return
    end
    if flags[:oil_missing]
      return(
        say(
          "Daro: Ask Harker at the north-eastern ring about the missing oil. Look at his new lanterns."
        )
      )
    end
    say(
      "Daro: My shoulder gave out unloading the Salt Thread. The clerk kept me on to count.",
      "Daro: The island manifest says twelve flour sacks and six oil tins. Read the three cargo labels along the waterfront, would you?"
    )
    flags[:cargo_started] = true
    return unless CARGO.keys.all? { |id| flags.fetch(:counted, {})[id] }
    answer =
      pbMessage("Daro: What is short?", ["Flour", "Lamp oil", "Nothing", "Let me check again"], 4)
    return if answer == 3 || answer < 0
    if answer != 1
      return say("Daro: Count the three lots together. I will leave the manifest here.")
    end
    flags[:oil_missing] = true
    say(
      "Daro: Five tins. Harker carried something up to the ring just before I arrived.",
      "Daro: Ask him. Quietly. I would rather have the oil than a fight."
    )
  end

  def harker
    if flags[:oil_missing] && !flags[:oil_returned]
      say(
        "Harker: The tin? Borrowed. The crowd cannot bet in the dark.",
        "You point to PSYDUCK ISLAND on the shipping label.",
        "Harker: ...All right. It has not been opened. Venn! Take it back to the east lot."
      )
      flags[:oil_returned] = true
      return say("A sailor carries the sealed tin towards the cargo. Daro will want to know.")
    end
    say("Harker: I used to call the watches. Now I call the bouts. Same lungs. Better tips.")
    choice =
      pbMessage(
        "Harker taps the challenger's slate.",
        ["Meet the challenger", "Ask about the ring", "Leave"],
        3
      )
    if choice == 0
      Tidebound::DockRing.challenge
    elsif choice == 1
      Tidebound::DockRing.board
    end
  end

  TALKS = {
    bettor: [
      "Venn: Three coins on the long legs. No, two. The third is for supper.",
      "Venn: Do not look at me like that. I have already lost supper once."
    ],
    veteran: [
      "Edda: My Machoke hauled barrels for eleven years. When his knee went, the owner offered me half a week's wages for him.",
      "Edda: I took him home. We are both slow on stairs now."
    ],
    spectator: [
      "Rusk: I know which one is tired. Watch the feet.",
      "Rusk: That is not the same as knowing which one will lose."
    ],
    cook: [
      "Neris: I feed the late watch from this stall. Hot broth, cold bread, the same argument about the price.",
      "Neris: When my husband stopped coming home, they kept bringing his bowl back washed. I still put it out."
    ],
    apprentice: [
      "Pell: Sella makes me undo a knot if I cannot explain what holds it.",
      "Pell: I thought she was being cruel. Then a man stood on my first net."
    ]
  }.freeze

  def talk(id)
    say(*TALKS.fetch(id))
  end

  def notice
    say(
      "ODD JOBS: Jory has an undelivered letter. Sella needs a netting shuttle. Daro wants the island cargo counted.",
      "Across the bottom: KEEP THE BETTING MONEY OUT OF THE FLOUR TIN."
    )
  end
end
