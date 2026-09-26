const { createHarness } = require('./support/ruby_vm.cjs');

(async () => {
  const h = await createHarness();
  h.loadEngine();
  h.loadData();
  h.ruby('src/014_RegionalForms.rb');
  h.ruby('tests/regional_snakes.rb');
  h.finish();
})().catch(error => { console.error(String(error)); process.exitCode = 1; });
