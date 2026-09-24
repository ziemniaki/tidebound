const fs = require('node:fs');
const path = require('node:path');
const { DefaultRubyVM } = require('@ruby/wasm-wasi/dist/node');

(async () => {
  const binary = fs.readFileSync(require.resolve('@ruby/3.2-wasm-wasi/dist/ruby.wasm'));
  const module = await WebAssembly.compile(binary);
  const { vm } = await DefaultRubyVM(module);
  const root = path.resolve(__dirname, '..');
  const files = [
    'Tests/001_Support.rb',
    '001_Core.rb',
    '002_Essentials.rb',
    'Tests/002_CoreTests.rb',
    'Tests/003_AdapterTests.rb'
  ];
  for (const file of files) {
    const code = fs.readFileSync(path.join(root, file), 'utf8');
    const encoded = Buffer.from(code, 'utf8').toString('base64');
    vm.eval('eval(' + JSON.stringify(encoded) + '.unpack1("m0").force_encoding("UTF-8"), TOPLEVEL_BINDING, ' + JSON.stringify(file) + ')');
  }
  vm.eval('$stdout.flush; $stderr.flush');
})().catch(error => { console.error(String(error)); process.exitCode = 1; });
