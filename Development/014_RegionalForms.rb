# New southern-road encounters use the local form. Owned Pokemon are never rewritten.
EventHandlers.add(:on_wild_pokemon_created, :tidebound_sunkern,
  proc { |pkmn|
    next unless $game_map && $game_map.map_id == 108
    next unless pkmn.species == :SUNKERN && pkmn.form_simple == 0
    pkmn.form = 1
    pkmn.reset_moves
  }
)

# Moonkern declares DefaultForm_0 in species data, so evolution resets form safely.

# New northern-forest Wurmple use the local form. Existing companions stay intact.
EventHandlers.add(:on_wild_pokemon_created, :tidebound_wurmple,
  proc { |pkmn|
    next unless $game_map && $game_map.map_id == 103
    next unless pkmn.species == :WURMPLE && pkmn.form_simple == 0
    pkmn.form = 1
  }
)

# Glaciverm and the provisional Frostcoon declare DefaultForm_0. Native
# evolution normalizes their form. The split uses the existing Silcoon/Cascoon
# methods and each individual's personal ID, never a new roll on level gain.

# Shore Psyduck keep their familiar appearance and newly gain Psychic typing.
# A captured regional Psyduck is not changed when the player leaves this map;
# older owned Psyduck still evolve into ordinary Golduck as they did before.
EventHandlers.add(:on_wild_pokemon_created, :tidebound_psyduck,
  proc { |pkmn|
    next unless $game_map && $game_map.map_id == 108
    next unless pkmn.species == :PSYDUCK && pkmn.form_simple == 0
    pkmn.form = 1
    pkmn.reset_moves
  }
)
