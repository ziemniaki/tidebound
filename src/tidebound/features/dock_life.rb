# Small, independent dockside errands. Saved in the shared story object.
module Tidebound::DockLife
  module_function
  def state
    Tidebound.story[:dock_life] ||= {}
  end
  def say(*lines)
    lines.each { |line| pbMessage(line) }
  end
  def reward(key, item, quantity, line)
    return if state[key]
    unless $bag.add(item, quantity)
      say("Make a little room in your bag. I'll keep this for you.")
      return
    end
    state[key] = true
    say(line, _INTL("Received {1} {2}.", quantity, GameData::Item.get(item).name))
  end
  def sailmaker
    if state[:sail_paid]
      say(
        "Ada: My sister made the first sail I ever mended. Now I mend her daughter's.",
        "Good work outlives the hands. Usually by several repairs."
      )
    elsif state[:canvas]
      reward(
        :sail_paid,
        :SILKSCARF,
        1,
        "Ada: Just the cloth I needed. Here, a scarf from the offcuts. My sister taught me never to waste the soft bits."
      )
      $bag.remove(:TBDOCKCANVAS) if state[:sail_paid]
    else
      say(
        "Ada: That sail belongs to my niece. She won't leave without it, and I won't send her out with this tear.",
        "There's dry canvas in a marked bundle beside the customs shed. Would you fetch it? My knee won't bear the quay steps."
      )
      state[:canvas_requested] = true
    end
  end
  def canvas
    if state[:sail_paid] || state[:canvas]
      say("The remaining bundles are damp. Someone has laid them out to dry.")
    elsif state[:canvas_requested]
      if $bag.add(:TBDOCKCANVAS)
        state[:canvas] = true
        say("You lift the dry canvas out of its oilskin wrapping. Ada can use this.")
      else
        say("Your bag is too full for the canvas.")
      end
    else
      say("A bundle marked 'ADA - KEEP DRY'. You leave it wrapped.")
    end
  end
  def courier
    if state[:letter_delivered]
      say(
        "Ivo: You found him? Good. I was beginning to think a letter could grow old in your pocket."
      )
    elsif state[:letter]
      say("Ivo: Eda's father, Tomas. The old fellow by the northern houses. The letter's for him.")
    else
      say(
        "Ivo: I've carried this through three harbours. 'Father, the docks.' Wonderful address.",
        "His name's Tomas. Used to mend nets, they tell me. Will you take it to him?"
      )
      return unless pbConfirmMessage("Deliver the letter to Tomas?")
      if $bag.add(:TBDOCKLETTER)
        state[:letter] = true
        say("Ivo: Keep the seal dry. She's written enough on the outside already.")
      else
        say("Ivo: Make room first. No sense losing it now.")
      end
    end
  end
  def tomas
    if state[:letter] && !state[:letter_delivered]
      say(
        "Tomas: Eda? ...Would you hold the lamp? My eyes aren't what they were.",
        "He reads the same line twice. Then smooths the paper with his thumb.",
        "Tomas: She's opened her own bakery. Says the first batch was dreadful.",
        "I taught her that recipe. I'll have to write and take the blame."
      )
      state[:letter_delivered] = true
      $bag.remove(:TBDOCKLETTER)
    elsif !state[:letter_delivered]
      say(
        "Tomas: I used to mend every net on this quay. Now they bring me the ones they can't untangle.",
        "Nice to be needed. Nicer if they'd bring a chair."
      )
    end
    if state[:letter_delivered]
      reward(:letter_paid, :ORANBERRY, 3, "Tomas: For your road. I was saving them for somebody.")
    end
    deliver_meal(:tomas, "Tomas: Ah, she remembered I can't chew the crusts. Tell her I noticed.")
  end
  def cook
    if state[:meal_paid]
      say(
        "Mara: My father cooked for twenty on a stove this size. I manage six and complain twice as much."
      )
    elsif state[:meals] && state[:meals].length == 3
      reward(
        :meal_paid,
        :SITRUSBERRY,
        2,
        "Mara: Empty bowls. Best compliment a cook gets. These are for you."
      )
      $bag.remove(:TBDOCKMEALS) if state[:meal_paid]
    elsif state[:meals]
      say(
        "Mara: #{3 - state[:meals].length} bowls left. Tomas up north, Lio by the lamps, Sen at the nets."
      )
    else
      say(
        "Mara: They work through the meal bell and wonder why their hands shake.",
        "Could you take bowls to Tomas, Lio and Sen? Nothing grand. Fish stew, mostly potatoes."
      )
      return unless pbConfirmMessage("Take the three covered bowls?")
      if $bag.add(:TBDOCKMEALS)
        state[:meals] = []
        say("Mara tucks a folded cloth around the bowls. 'Mind your fingers.'")
      else
        say("Mara: You'll need a little room for the basket.")
      end
    end
  end
  def deliver_meal(person, line)
    return unless state[:meals] && !state[:meals].include?(person)
    say("You pass over a covered bowl.", line)
    state[:meals] << person
    say("The bowls are empty. Take them back to Mara.") if state[:meals].length == 3
  end
  def lamplighter
    say(
      "Lio: I was a deckhand until I lost my balance. Nothing dramatic. It just never came back.",
      "These lamps stay still. Most evenings, so do I."
    )
    deliver_meal(:lio, "Lio: Still warm! I'll sit for a minute. The lamps can manage without me.")
  end
  def netmender
    say(
      "Sen: That little knot? My husband ties them left-handed. I can find his work in a whole pile.",
      "He's on the late watch. I leave a loose end so he knows where to start."
    )
    deliver_meal(:sen, "Sen: Mara puts too much pepper in. Don't tell her I like it.")
  end
  def spectator(id)
    lines = {
      wager: [
        "Sailor: Two coppers on the long legs. No, three. ...Don't tell the cook.",
        "He counts his remaining coins twice."
      ],
      scar: [
        "Sailor: That Machop used to shift cargo with me. See the nick in its ear?",
        "A snapped pulley. Before all this. It still comes when I whistle."
      ],
      loser: ["Sailor: Lost my supper money. Again.", "The cheering starts. He doesn't join in."],
      watcher: [
        "Sailor: They call it practice. Practice doesn't usually need a man collecting bets."
      ]
    }
    say(*lines.fetch(id))
  end
end
