const { createHarness } = require('./support/ruby_vm.cjs');
(async () => {
  const h = await createHarness();
  h.ruby('tests/support/sprite_services.rb');
  h.ruby('src/tidebound/presentation/sprites.rb');
  h.ruby('src/generated/world_registry.rb');
  h.ruby('src/tidebound/features/actors.rb');
  h.ruby('tests/presentation_support.rb');
  h.finish();
})().catch(error => { console.error(String(error)); process.exitCode = 1; });
