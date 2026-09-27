const fs = require('node:fs');
const path = require('node:path');
const { DefaultRubyVM } = require('@ruby/wasm-wasi/dist/node');

const root = path.resolve(__dirname, '../..');
const references = path.join(root, 'tests/engine_reference');

// Share compilation, never Ruby state: doubles in one suite must not leak into another.
let compiled;
async function createHarness() {
  compiled ||= WebAssembly.compile(fs.readFileSync(require.resolve('@ruby/3.2-wasm-wasi/dist/ruby.wasm')));
  const { vm } = await DefaultRubyVM(await compiled);
  const entries = JSON.parse(fs.readFileSync(path.join(references, 'index.json'), 'utf8'));

  function evaluate(code, name) {
    const encoded = JSON.stringify(Buffer.from(code).toString('base64'));
    try {
      vm.eval(`eval(${encoded}.unpack1("m0").force_encoding("UTF-8"), TOPLEVEL_BINDING, ${JSON.stringify(name)})`);
    } catch (error) {
      throw new Error(`Ruby fixture ${name}: ${error}`);
    }
  }

  function ruby(file) {
    evaluate(fs.readFileSync(path.join(root, file), 'utf8'), file);
  }

  function engine(...names) {
    for (const name of names) {
      const matches = entries.filter(entry => entry.key === name);
      if (matches.length !== 1) throw new Error(`Expected one engine script named ${name}`);
      ruby(`tests/engine_reference/${matches[0].file}`);
    }
  }

  function loadEngine() {
    ruby('tests/support/domain_boot.rb');
    engine(...require('./engine_scripts.json'));
  }

  function loadData() {
    for (const name of ['species', 'species_metrics', 'moves', 'abilities', 'items',
      'types', 'trainer_types', 'metadata', 'player_metadata', 'map_metadata', 'encounters']) {
      const file = `${name}.dat`;
      const encoded = fs.readFileSync(path.join(root, 'game/Data', file)).toString('base64');
      evaluate(`GameData.constants.each do |name|
  klass = GameData.const_get(name)
  next unless klass.is_a?(Class) && klass.const_defined?(:DATA_FILENAME)
  next unless klass::DATA_FILENAME == ${JSON.stringify(file)}
  klass.const_set(:DATA, Marshal.load(${JSON.stringify(encoded)}.unpack1("m0")))
end`, file);
    }
    const dex = fs.readFileSync(path.join(root, 'game/Data/regional_dexes.dat')).toString('base64');
    evaluate(`def load_data(file)
  return Marshal.load(${JSON.stringify(dex)}.unpack1("m0")) if file == "Data/regional_dexes.dat"
  raise "Unmapped fixture data: #{file}"
end`, 'data bridge');
  }

  function production() {
    const custom = entries.filter(entry => entry.name.startsWith('Tidebound/'));
    if (!custom.length) throw new Error('No embedded game scripts');
    for (const entry of custom) ruby(`tests/engine_reference/${entry.file}`);
    console.log(`Loaded all ${custom.length} game scripts in archive order.`);
  }

  function compileEvents() {
    const source = process.env.TIDEBOUND_EVENT_SCRIPTS || path.join(root, 'tools/generated/event_scripts.json');
    const events = JSON.parse(fs.readFileSync(source, 'utf8'));
    for (const event of events) {
      evaluate(`RubyVM::InstructionSequence.compile(${JSON.stringify(event.code)}, ${JSON.stringify(event.name)})`, event.name);
      for (const match of event.code.matchAll(/\b(Tidebound(?:::[A-Z]\w*)+)\.([a-z_]\w*[!?]?)/g)) {
        evaluate(`raise "Unknown event API: ${match[1]}.${match[2]}" unless ${match[1]}.respond_to?(:${match[2]})`, event.name);
      }
    }
    console.log(`Compiled ${events.length} native event bodies.`);
  }

  return { evaluate, ruby, engine, loadEngine, loadData, production, compileEvents,
    finish: () => evaluate('$stdout.flush; $stderr.flush', 'flush') };
}

module.exports = { createHarness };
