$player=Player.new("Ren", :POKEMONTRAINER_Red)
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
