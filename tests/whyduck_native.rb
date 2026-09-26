# TEST ONLY. Run under offscreen Linux mkxp-z with the chosen-party legacy save.
$stdout.sync=true
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('chosen-party.rxdata'))
  end
end
module WhyduckNativeCheck
  def update
    super
    return if $tb_whyduck_checked || !$player || !$game_map || !$game_system
    $tb_whyduck_checked=true
    run_whyduck_check
  end
  def run_whyduck_check
    base=GameData::Species.get(:PSYDUCK)
    form=GameData::Species.get_species_form(:PSYDUCK,1)
    why=GameData::Species.get(:WHYDUCK)
    raise 'base Psyduck changed' unless base.types==[:WATER] && base.get_evolutions.first[0]==:GOLDUCK
    raise 'regional typing' unless form.types==[:WATER,:PSYCHIC]
    raise 'regional evolution data' unless form.get_evolutions.first==[:WHYDUCK,:Level,16]
    raise 'Whyduck types/stats' unless why.types==[:WATER,:PSYCHIC] && why.base_stats[:SPECIAL_ATTACK]==130 && why.base_stats[:SPECIAL_DEFENSE]==115
    metrics=GameData::SpeciesMetrics.get_species_form(:WHYDUCK,0)
    raise 'Whyduck metrics' unless metrics && metrics.front_sprite==[1,13] && metrics.back_sprite==[0,5]
    raise 'Whyduck sprite' unless GameData::Species.front_sprite_filename(:WHYDUCK)&.end_with?('WHYDUCK.png')
    raise 'Whyduck backsprite' unless GameData::Species.back_sprite_filename(:WHYDUCK)&.end_with?('WHYDUCK.png')
    old_pokemon=Pokemon.new(:PSYDUCK,33)
    raise 'old save evolution path' unless old_pokemon.check_evolution_on_level_up==:GOLDUCK
    Tidebound::Opening.travel(108,20,11)
    wild=Pokemon.new(:PSYDUCK,15)
    EventHandlers.trigger(:on_wild_pokemon_created,wild)
    raise 'shore spawn regional' unless wild.form==1 && wild.types==[:WATER,:PSYCHIC]
    wild.level=16
    raise 'native evolution' unless wild.check_evolution_on_level_up==:WHYDUCK
    wild.species=:WHYDUCK
    raise 'form leak' unless wild.form==0 && wild.baseStats[:SPECIAL_ATTACK]==130 && wild.baseStats[:SPECIAL_DEFENSE]==115
    raise 'other game quest altered' unless $player.party.any?
    File.write('WHYDUCK_NATIVE_PASS.txt','PASS: old saved party; ordinary and regional types; road spawn; level 16 evolution; stats; sprite paths.\n')
    puts 'WHYDUCK_NATIVE_PASS'
    exit
  end
end
Scene_Map.prepend(WhyduckNativeCheck)
