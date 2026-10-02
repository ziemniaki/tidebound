# The city's little refuge is a place of ordinary care, without a quest gate.
module Tidebound::DocksPark
  module_function

  def say(*lines)
    lines.each { |line| pbMessage(line) }
  end

  def monument
    statue = Tidebound::World.actor(:park_monument)
    Tidebound::World.camera_to(statue.x, statue.y - 2) if statue
    say(
      "SUICUNE\nProtector of this land. Beloved keeper of harmony.",
      "Below the worn inscription: In the heart of the forest, may you find rest.",
      "Many hands have polished the stone beneath his paws."
    )
  ensure
    Tidebound::World.camera_home if statue && $game_map.map_id == statue.map_id
  end

  TALKS = {
    mara: [
      "Mara cups her hands around a little candle until the wick catches.",
      "Mara: My boy went inland with the timber cart. Three watches, they said.",
      "Mara: I don't ask Suicune to hurry him. Just let him be somewhere warm."
    ],
    toven: [
      "Toven lays two small flowers beside the stone.",
      "Toven: My sister and I haven't spoken since we buried our father. We argued over a bowl.",
      "Toven: Suicune brings things into harmony. I'd settle for knowing how to knock."
    ],
    lina: [
      "Lina: They say he lives in the heart of the forest. I've never seen him. I still bring bread.",
      "Lina: My old Growlithe cries in his sleep. He used to dream with his paws.",
      "Lina: Just one quiet night. That's all I came to ask."
    ],
    keeper: [
      "Orren: Don't pull up the flowers by the path. Someone waters them before each watch.",
      "Orren: My wife used to tend this place. I thought I'd stop coming when she was gone.",
      "Orren: Then I found someone had watered her flowers. So I brought the broom."
    ]
  }.freeze

  def talk(id)
    say(*TALKS.fetch(id))
  end

  def offerings
    say(
      "Little candles, two flowers and a piece of bread. Nothing here was bought to impress anyone.",
      "The clay bowl holds a little bread. Someone has left the softer half."
    )
  end

  def bench
    say("The bench has been mended with a different wood. There is room for someone beside you.")
  end
end
