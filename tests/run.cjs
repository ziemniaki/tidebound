const { createHarness } = require('./support/ruby_vm.cjs');

const suites = {
  battles(h) {
    for (const file of [
      'tests/support/battle_services.rb',
      'src/tidebound/domain/state.rb', 'src/tidebound/engine/battles.rb',
      'tests/gameplay/state.rb', 'tests/gameplay/battles.rb'
    ]) h.ruby(file);
  },
  gameplay(h) {
    h.loadEngine();
    h.loadData();
    h.ruby('tests/support/world_services.rb');
    h.engine('SaveData', 'SaveData_Value', 'PokemonBag', 'Interpreter', 'Game_SaveValues');
    h.ruby('tests/support/integration_services.rb');
    h.production();
    h.checkScripts();
    h.ruby('tests/tooling/api_checks.rb');
    h.ruby('tests/support/scene_services.rb');
    h.ruby('tests/support/story_helpers.rb');
    for (const suite of [
      'companions', 'opening', 'neighbor', 'hideout', 'interaction', 'world', 'scenes', 'regional_snakes', 'harbour'
    ]) h.ruby(`tests/gameplay/${suite}.rb`);
  },
  presentation(h) {
    h.engine('Event_Handlers', 'Event_HandlerCollections');
    h.ruby('tests/support/sprite_services.rb');
    h.ruby('src/tidebound/presentation/sprites.rb');
    h.ruby('src/generated/world_registry.rb');
    h.ruby('tests/gameplay/presentation.rb');
  }
};

(async () => {
  const selected = process.argv.slice(2);
  for (const name of selected.length ? selected : Object.keys(suites)) {
    if (!Object.hasOwn(suites, name)) throw new Error(`Unknown suite ${name}; choose ${Object.keys(suites).join(', ')}`);
    console.log(`\nRuby: ${name}`);
    const h = await createHarness();
    try { suites[name](h); } finally { h.finish(); }
  }
})().catch(error => { console.error(String(error)); process.exitCode = 1; });
