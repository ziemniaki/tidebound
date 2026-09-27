# Only newly created wild Pokémon receive map-local forms; owned individuals stay intact.
EventHandlers.add(
  :on_wild_pokemon_created,
  :tidebound_regional_forms,
  proc do |pokemon|
    next unless $game_map && pokemon.form_simple == 0
    form = Tidebound::WILD_FORMS.dig($game_map.map_id, pokemon.species.to_s)
    next unless form
    pokemon.form = form
    pokemon.reset_moves
  end
)
