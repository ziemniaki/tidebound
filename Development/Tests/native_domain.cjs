const fs=require('fs'),path=require('path');
const {DefaultRubyVM}=require('@ruby/wasm-wasi/dist/node');
(async()=>{
 const mod=await WebAssembly.compile(fs.readFileSync(require.resolve('@ruby/3.2-wasm-wasi/dist/ruby.wasm')));
 const {vm}=await DefaultRubyVM(mod);
 function run(code,name){try {vm.eval(`eval(${JSON.stringify(Buffer.from(code).toString('base64'))}.unpack1("m0").force_encoding("UTF-8"), TOPLEVEL_BINDING, ${JSON.stringify(name)})`);}catch(e){console.error('AT '+name);throw e;}}
 const root=path.resolve(__dirname,'../..'),ref=path.join(__dirname,'engine_reference'),dev=path.join(root,'Development');
 run(`$VERBOSE=nil
module System
 def self.data_directory; '/'; end
 def self.user_language; 'en'; end
end
module MessageTypes
 def self.const_missing(n); n; end
end
def pbGetMessageFromHash(kind, value); value; end
def pbGetMessage(kind,value); value.to_s; end
def _INTL(s,*args); args.each_with_index { |v,i| s=s.gsub("{#{i+1}}",v.to_s) }; s; end
def pbGetLanguage; 2; end
def nil_or_empty?(v); v.nil? || v.empty?; end
module MultipleForms
 def self.call(*args); nil; end
end
`, 'domain_boot');
 const nums=[0,1,15,100,...Array.from({length:40},(_,i)=>103+i),273,274,275,276,277,286,287,289,290,362,363];
 for(const num of nums){const file=fs.readdirSync(ref).find(x=>x.startsWith(String(num).padStart(3,'0')+'_'));if(file)run(fs.readFileSync(path.join(ref,file),'utf8'),file);}
 for(const file of fs.readdirSync(path.join(root,'Data')).filter(x=>x.endsWith('.dat'))){
  if(['species.dat','species_metrics.dat','moves.dat','abilities.dat','items.dat','types.dat','trainer_types.dat','metadata.dat','player_metadata.dat','map_metadata.dat'].includes(file)){
   const b64=fs.readFileSync(path.join(root,'Data',file)).toString('base64');
   run(`GameData.constants.each do |name|
 c=GameData.const_get(name)
 next unless c.is_a?(Class) && c.const_defined?(:DATA_FILENAME) && c::DATA_FILENAME==${JSON.stringify(file)}
 c.const_set(:DATA,Marshal.load(${JSON.stringify(b64)}.unpack1("m0")))
end`,file);
  }
 }

 const dex=fs.readFileSync(path.join(root,'Data/regional_dexes.dat')).toString('base64');
 run(`def load_data(file); return Marshal.load(${JSON.stringify(dex)}.unpack1("m0")) if file=="Data/regional_dexes.dat"; raise "Unmapped native file: #{file}"; end`, 'test_file_bridge');
 run(fs.readFileSync(path.join(dev,'001_Core.rb'),'utf8'),'Tidebound core');
 run(`$player=Player.new("Ren", :POKEMONTRAINER_Red)
$player.character_ID=1
p=Pokemon.new(:NATU,7,$player)
p.name="Wick"; p.item=:MYSTICWATER
p.learn_move(:PECK)
s=Tidebound::State.new
id=s.assign_identity(p)
p.hp=0
before=Marshal.dump(p)
s.enter_astral!([p],{:map_id=>103,:x=>27,:y=>10})
foe=s.begin_encounter!(id)
raise "spirit identity changed" unless Tidebound.identity(foe)==id
raise "item clone" unless foe.item.nil?
raise "opponent not restored" unless foe.hp==foe.totalhp
restored=s.recover!(id)
raise "wrong HP" unless restored.hp==(restored.totalhp*0.25).ceil
raise "wrong identity" unless Tidebound.identity(restored)==id
raise "lost item" unless restored.item_id==:MYSTICWATER
raise "changed owner" unless Marshal.dump(restored.owner)==Marshal.dump(p.owner)
raise "changed moves" unless Marshal.dump(restored.moves)==Marshal.dump(p.moves)
raise "changed IVs" unless restored.iv==p.iv
s.leave_astral!
restored.status=:POISON
restored.moves.each { |m| m.pp=0 }
20.times { s.rest!([restored]) }
raise "rest cumulative" unless restored.hp==(restored.totalhp*0.25).ceil
raise "rest cured poison" unless restored.status==:POISON
raise "PP floor" unless restored.moves.all? { |m| m.pp==1 }
roundtrip=Marshal.load(Marshal.dump(s))
raise "save lost identity" unless roundtrip.souls.first.id==id
puts "PASS: actual Essentials Pokemon/Move/Owner/Player objects; capture copy, identity, HP, status, PP and Marshal persistence."
`, 'actual_pokemon_roundtrip');

 run(fs.readFileSync(path.join(__dirname,'opening_smoke.rb'),'utf8'),'opening fixtures');
 for(const n of [24,25,270,33]) {
  const f=fs.readdirSync(ref).find(x=>x.startsWith(String(n).padStart(3,'0')+'_'));
  run(fs.readFileSync(path.join(ref,f),'utf8'),f);
 }
 run(fs.readFileSync(path.join(dev,'002_Essentials.rb'),'utf8'),'adapter');
 const saveValues=fs.readFileSync(path.join(ref,'027_Game_SaveValues.rb'),'utf8');
 for(const id of ['player','bag']) {
  const block=saveValues.match(new RegExp('SaveData.register\\(:'+id+'\\) do[\\s\\S]*?\\nend'));
  if(!block)throw new Error('Missing native save registration '+id);
  run(block[0], 'native save registration '+id);
 }
 run(fs.readFileSync(path.join(dev,'003_MapPassages.rb'),'utf8'),'passages');
 run(fs.readFileSync(path.join(dev,'004_Opening.rb'),'utf8'),'opening');
 run(fs.readFileSync(path.join(dev,'006_FirstWalk.rb'),'utf8'),'first walk');
 run(fs.readFileSync(path.join(dev,'007_Coast.rb'),'utf8'),'coast');
 run('module Tidebound; module Opening; def self.coast_camera_home; end; end; end','camera fixture');
 run(fs.readFileSync(path.join(dev,'008_NeighborQuest.rb'),'utf8'),'neighbor quest');
 run(fs.readFileSync(path.join(dev,'010_FieldDetails.rb'),'utf8').split('# The generated maps')[0],'field domain rules');
 run(fs.readFileSync(path.join(__dirname,'opening_flow.rb'),'utf8'),'opening flow');
 run(fs.readFileSync(path.join(__dirname,'neighbor_flow.rb'),'utf8'),'neighbor flow');
 run(fs.readFileSync(path.join(dev,'023_Hideout.rb'),'utf8'),'hideout');
 run(fs.readFileSync(path.join(__dirname,'hideout_flow.rb'),'utf8'),'hideout flow');
 // RubyVM compiler checks event bodies and custom integration, no graphics needed.
 for(const file of fs.readdirSync(dev).filter(x=>/^\d{3}_.*\.rb$/.test(x))){const code=fs.readFileSync(path.join(dev,file),'utf8');run(`RubyVM::InstructionSequence.compile(${JSON.stringify(Buffer.from(code).toString('base64'))}.unpack1("m0"),${JSON.stringify(file)})`,file+' syntax');}
 const events=JSON.parse(fs.readFileSync(path.join(dev,'event_scripts.json'),'utf8'));
 for(const ev of events)run(`RubyVM::InstructionSequence.compile(${JSON.stringify(Buffer.from(ev.code).toString('base64'))}.unpack1("m0"),${JSON.stringify(ev.name)})`,ev.name+' syntax');
 run(`puts "PASS: ${fs.readdirSync(dev).filter(x=>/^\d{3}_.*\.rb$/.test(x)).length} custom scripts and ${events.length} native event scripts compile."; $stdout.flush; $stderr.flush`,'done');
})().catch(e=>{console.error(String(e));process.exitCode=1});
