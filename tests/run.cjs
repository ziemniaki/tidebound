const { createHarness } = require('./support/ruby_vm.cjs');

(async () => {
  const h = await createHarness();
  for (const file of [
    'tests/001_Support.rb', 'src/001_Core.rb', 'src/002_Essentials.rb',
    'tests/002_CoreTests.rb', 'tests/003_AdapterTests.rb'
  ]) h.ruby(file);
  h.finish();
})().catch(error => { console.error(String(error)); process.exitCode = 1; });
