// Syntax Tree runs on the same locked Ruby WASM runtime as the headless suites.
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const { WASI } = require('node:wasi');
const { RubyVM } = require('@ruby/wasm-wasi');

(async () => {
  const cache = path.resolve(process.argv[2]);
  const check = process.argv.includes('--check');
  const binary = fs.readFileSync(require.resolve('@ruby/3.2-wasm-wasi/dist/ruby.wasm'));
  const wasi = new WASI({ version: 'preview1', returnOnExit: true, preopens: { '/formatter': cache } });
  const { vm } = await RubyVM.instantiateModule({ module: await WebAssembly.compile(binary), wasip1: wasi });
  vm.eval('$LOAD_PATH.unshift(*Dir["/formatter/*/lib"]); load "/formatter/ripper-core.rb"; require "rubygems/version"; require "syntax_tree"');
  const files = execFileSync('git', ['ls-files', '-z', 'src/tidebound', 'tests', 'tools'], { encoding: 'utf8' })
    .split('\0').filter(file => file.endsWith('.rb'));
  let changed = 0;
  for (const file of files) {
    const source = fs.readFileSync(file, 'utf8');
    const encoded = Buffer.from(source).toString('base64');
    const formatted = vm.eval(`SyntaxTree.format(${JSON.stringify(encoded)}.unpack1("m0").force_encoding("UTF-8"), 100)`).toString();
    if (source === formatted) continue;
    changed += 1;
    if (check) console.error('Needs formatting: ' + file);
    else fs.writeFileSync(file, formatted);
  }
  console.log(`${files.length} Ruby files checked; ${changed} ${check ? 'need formatting' : 'formatted'}.`);
  if (check && changed) process.exitCode = 1;
})().catch(error => { console.error(String(error)); process.exitCode = 1; });
