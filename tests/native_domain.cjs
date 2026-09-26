const { createHarness } = require('./support/ruby_vm.cjs');

(async () => {
  const h = await createHarness();
  h.loadEngine();
  h.loadData();
  h.ruby('tests/opening_smoke.rb');
  h.engine('SaveData', 'SaveData_Value', 'PokemonBag', 'Interpreter', 'Game_SaveValues');
  h.ruby('tests/support/integration_services.rb');
  h.production();
  h.ruby('tests/support/scene_services.rb');
  for (const suite of [
    'actual_pokemon_roundtrip', 'regional_evolution_thresholds', 'field_encounter_rosters',
    'opening_flow', 'neighbor_flow', 'hideout_flow', 'save_format', 'interaction_flow'
  ]) h.ruby(`tests/${suite}.rb`);
  h.compileEvents();
  h.finish();
})().catch(error => { console.error(String(error)); process.exitCode = 1; });
