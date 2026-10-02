# Harbour conversations, optional battles and passage to the next chapter.
module Tidebound::Docks
  module_function
  def flags
    # Preserve the persisted key so existing saves retain their harbour progress.
    Tidebound.story[:demo_launch] ||= {}
  end
  def say(*lines)
    lines.each { |line| pbMessage(line) }
  end
  TALKS = {
    ropes: [
      "Sailor: A rope has a memory. Coil it badly and it'll remind you when you need it most.",
      "This one remembers three captains. None of them could coil it."
    ],
    keeper: [
      "Sailor: You're the keeper's child? We look for your mother's light before anything else.",
      "Tell her the crew of the Little Promise said thank you. She'll say she only turns a handle. Don't believe her."
    ],
    flour: [
      "Sailor: Flour, lamp oil, spare hinges. That's the cargo.",
      "People ask what wonders I've brought from across the sea. Mostly hinges."
    ],
    stars: [
      "Sailor: We reckon our watches by the bells. Six bells, then the next pair take over.",
      "The sky doesn't always give you much help out here."
    ],
    letters: [
      "Sailor: I carry letters in this tin. Wax around the lid keeps them dry.",
      "Some villages only have one person left who gets a letter. We still stop."
    ],
    cargo: [
      "Sailor: Buy a crate without asking whose it is, and somebody inland goes hungry.",
      "Cheap goods have a story. Ask for it."
    ],
    museum: [
      "Sailor: The museum keeps things we pull from old wrecks. Tools, bowls, a blade nobody here could lift gracefully.",
      "I go for the little clay boats. Someone made those for a child."
    ],
    snow: [
      "Sailor: The mountain folk trade good rope for salt. Their young warriors bow before they help unload.",
      "Makes it awkward when you drop a sack on your foot and start swearing."
    ],
    pie: [
      "Sailor: I used to bring a pie back from City 4 on every crossing.",
      "Used to. The new mate found where I hid it."
    ],
    sleep: [
      "Sailor: We take turns sleeping, even in harbour. Someone has to mind the moorings.",
      "My turn's next. Unless you ask me another question."
    ],
    islands: [
      "Sailor: Psyduck Island? Plenty of ducks, yes. Very poor company when you've got a headache.",
      "They stand along the water as though they've forgotten what they came to say."
    ],
    repairs: [
      "Sailor: We patch this hull one board at a time. Not much of the first boat left.",
      "Still knows the way home, though."
    ],
    mate: [
      "Mate: The Little Promise is taking stores to Psyduck Island. Speak to our captain at the end of the eastern pier.",
      "Mind the ropes. They look harmless until you trip over one."
    ]
  }.freeze
  def talk(id)
    say(*TALKS.fetch(id))
  end
  BATTLES = {
    nell: {
      name: "Nell",
      team: [[:WINGULL, 8], [:WOOPER, 9]],
      invite:
        "Sailor Nell: I'm off watch. One friendly challenge, if you and your companions are ready?",
      loss: "Steady hands. I could learn from you."
    },
    oren: {
      name: "Oren",
      team: [[:POLIWAG, 10], [:KRABBY, 11]],
      invite: "Sailor Oren: We practise here before a long crossing. Care to join us for a battle?",
      loss: "A good lesson. Let's both remember it."
    }
  }.freeze
  def sailor_battle(id)
    if flags[id]
      say(
        (
          if id == :nell
            "Nell: Those little birds will brave a gale for each other. I try to be worthy of that."
          else
            "Oren: I promised to come home. Keeping a promise takes practice."
          end
        )
      )
      return
    end
    sailor = BATTLES.fetch(id)
    return unless pbConfirmMessage(sailor.fetch(:invite))
    return unless Tidebound::Encounters.able?
    result =
      Tidebound::Encounters.trainer(
        type: :SAILOR,
        name: sailor.fetch(:name),
        loss: sailor.fetch(:loss),
        team: sailor.fetch(:team),
        departure: "The harbour bells fall quiet."
      )
    if result == 1
      flags[id] = true
      say(sailor.fetch(:loss))
    end
  end
  def voyage
    say(
      "Captain: The Little Promise sails for Psyduck Island with the next watch.",
      "Captain: Room for one more, if you don't mind sharing the deck with the flour sacks."
    )
    return unless pbConfirmMessage("Join them for the voyage to Psyduck Island?")
    flags[:completed] = true
    say(
      "Captain: Then we'll keep a place for you. Take one last look around, eh?",
      "Beyond the harbour, the water carries a thin seam of silver.",
      "Your passage to Psyduck Island is arranged.\nThe crossing will open in a future chapter.",
      "You can keep exploring and save your journey. Speak to the captain again whenever you like."
    )
  end
end
