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
 const nums=[0,1,15,35,36,100,...Array.from({length:40},(_,i)=>103+i),273,274,275,276,277,286,287,289,290,362,363];
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
 run(fs.readFileSync(path.join(dev,'014_RegionalForms.rb'),'utf8'),'regional encounter hooks');
 run(`
$player=Player.new("Ren", :POKEMONTRAINER_Red)
$player.character_ID=1
$game_temp=Struct.new(:in_battle,:in_storage,:regional_dexes_data).new(false,false,nil)
$game_map=Struct.new(:map_id).new(108)
[:EKANS,:ARBOK].each do |id|
  ordinary=Pokemon.new(id,50,$player)
  saved_ordinary=Marshal.dump(ordinary)
  wild=Pokemon.new(id,5,$player)
  EventHandlers.trigger(:on_wild_pokemon_created,wild)
  raise "wrong form/types" unless wild.form_simple==1 && wild.types==[:NORMAL,:DARK]
  raise "wild poison move" if wild.moves.any? { |m| m.type==:POISON }
  data=wild.species_data
  pool=data.moves.map { |lv,m| m }+data.tutor_moves+data.get_egg_moves
  raise "Poison learnset" if pool.any? { |m| GameData::Move.get(m).type==:POISON }
  base=GameData::Species.get(id)
  raise "stats/abilities changed" unless data.base_stats==base.base_stats && data.abilities==base.abilities && data.hidden_abilities==base.hidden_abilities
  raise "ordinary companion changed" unless Marshal.dump(ordinary)==saved_ordinary && ordinary.types==[:POISON]
  wild.item=:ORANBERRY
  wild.hp=1
  wild.status=:PARALYSIS
  wild.moves.first.pp=0
  before=[wild.personalID,wild.owner.id,wild.item_id,wild.hp,wild.status,wild.moves.map { |m| [m.id,m.pp] }]
  restored=Marshal.load(Marshal.dump(wild))
  raise "save changed form" unless restored.form_simple==1
  after=[restored.personalID,restored.owner.id,restored.item_id,restored.hp,restored.status,restored.moves.map { |m| [m.id,m.pp] }]
  raise "save changed companion" unless before==after
end
snake=Pokemon.new(:EKANS,21,$player)
EventHandlers.trigger(:on_wild_pokemon_created,snake)
raise "early evolution" unless snake.check_evolution_on_level_up.nil?
snake.level=22
raise "missing level22 evolution" unless snake.check_evolution_on_level_up==:ARBOK
snake.species=:ARBOK
raise "lost evolved form" unless snake.form_simple==1 && snake.types==[:NORMAL,:DARK]
raise "poison egg inheritance" if snake.species_data.get_egg_moves.any? { |m| GameData::Move.get(m).type==:POISON }
$game_map.map_id=103
foreign=Pokemon.new(:EKANS,5,$player)
EventHandlers.trigger(:on_wild_pokemon_created,foreign)
raise "unrelated maps changed" unless foreign.form_simple==0
$game_map.map_id=108
other=Pokemon.new(:AIPOM,5,$player)
EventHandlers.trigger(:on_wild_pokemon_created,other)
raise "unrelated species changed" unless other.form_simple==0
puts "PASS: actual Essentials objects; wild forms/moves, level22 evolution, inherited egg moves, unchanged stats/abilities/ordinary forms, and save roundtrip."
$stdout.flush; $stderr.flush
`, 'regional_snakes');
})().catch(e=>{console.error(String(e));process.exitCode=1});
