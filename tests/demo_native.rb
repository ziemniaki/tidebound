# TEST ONLY. Native Linux engine, automated controls; never shipped in Scripts.
$stdout.sync=true
module DemoInput
  def trigger?(key)
    return Graphics.frame_count%4==0 if key==Input::USE
    super
  end
end
Input.singleton_class.prepend(DemoInput)
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('chosen-party.rxdata'))
  end
end
module DemoBattleWords
  def pbDisplayBrief(message,*args)
    ($demo_death_words ||= []) << message if message.include?('died') || message.include?('fainted')
    super
  end
end
Battle.prepend(DemoBattleWords)
module DemoNativeCheck
  def shot(name)
    12.times { Graphics.update;Input.update;updateSpritesets }
    b=Graphics.snap_to_bitmap;b.to_file("demo-#{name}.png");b.dispose
    puts "SHOT #{name}"
  end
  def update
    super
    return if @demo_check || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @demo_check=true
    o=Tidebound::Opening;d=Tidebound::DemoLaunch
    saved_party=$player.party.map(&:personalID);candies=$bag.quantity(:RARECANDY)
    o.travel_coast(22,12);shot('wooden-houses')
    raise 'village atlas' unless $game_map.tileset_name=='TideboundVillage'
    lights=$scene.spriteset.usersprites.find { |s|s.is_a?(TideboundWindowLights) }
    raise 'windows missing' unless lights && lights.instance_variable_get(:@sprites).sum { |s|s.pane_pixels.length }>0
    o.travel_coast(8,16);shot('lighthouse')
    o.travel(108,26,36);shot('psyduck')
    e=$game_map.events.values.find { |a|a.name=='Wild:PSYDUCK:shoreduck' }
    raise 'duck not added' unless e && e.x==27 && e.y==36
    pkmn=Pokemon.new(:PSYDUCK,15);EventHandlers.trigger(:on_wild_pokemon_created,pkmn)
    raise 'regional form' unless pkmn.form==1 && pkmn.types==[:WATER,:PSYCHIC]
    raise 'early evolution' if pkmn.check_evolution_on_level_up
    pkmn.level=16;raise 'level16 evolution' unless pkmn.check_evolution_on_level_up==:WHYDUCK
    pkmn.species=:WHYDUCK;raise 'evolution form leak' unless pkmn.form==0
    normal=Pokemon.new(:PSYDUCK,33);raise 'ordinary changed' unless normal.check_evolution_on_level_up==:GOLDUCK
    Tidebound::VaultVisit.q[:open]=true;Tidebound::VaultVisit.q[:talk]=true
    o.travel(112,26,47);shot('western-ship')
    raise 'new dock events' unless $game_map.events.values.count { |ev|ev.name.start_with?('Sailor ') }==15
    o.travel(112,55,47);shot('island-ship')
    raise 'night changed' unless PBDayNight.isNight? && $game_screen.tone.red==-80
    # Displaced old save at a new sailor position is safely relocated just once.
    d.flags.delete([:map_revision,112]);$game_player.moveto(55,49);d.safe_position
    raise 'old save remains blocked' unless Tidebound::MAP_PASSAGES[112][$game_player.y][$game_player.x]=='1'
    spot=[$game_player.x,$game_player.y];d.safe_position;raise 'repeat displacement' unless spot==[$game_player.x,$game_player.y]
    d.voyage;raise 'demo endpoint not reached' unless d.flags[:completed] && $game_map.map_id==112
    d.voyage # Repeating the ending must keep exploration available.
    raise 'party changed by demo scenes' unless $player.party.map(&:personalID)==saved_party && $bag.quantity(:RARECANDY)==candies
    raise 'save failed' unless Game.save('demo-complete.rxdata')
    data=SaveData.get_data_from_file('demo-complete.rxdata')
    raise 'demo flag absent from save' unless Marshal.dump(data).include?('demo_launch')
    if ENV['TB_DEMO_RENDER_ONLY']=='1'
      o.travel(112,50,39);shot('quay-objects')
      File.write('DEMO_RENDER_PASS.txt','Latest visual assets and 264-event map build rendered.');exit
    end
    # Actual native battles, with a strong test-only party to isolate flow.
    hero=Pokemon.new(:WHYDUCK,45);hero.moves.clear;hero.learn_move(:PSYCHIC);hero.learn_move(:SURF)
    $player.party.replace([hero]);Tidebound.state.checkpoint=[108,26,39,2]
    d.sailor_battle(:nell);raise 'Nell battle did not persist win' unless d.flags[:nell]
    hero.heal;d.sailor_battle(:oren);raise 'Oren battle did not persist win' unless d.flags[:oren]
    o.travel(108,26,36);hero.heal;d.psyduck
    raise 'overworld duck not cleared' unless Tidebound::NeighborQuest.q[:shoreduck_gone]
    raise 'wrong death message' unless $demo_death_words && $demo_death_words.length>=5 && $demo_death_words.all? { |m|m.include?('died') && !m.include?('fainted') }
    # Readable two-line caption; geometry and goal of minigame remain untouched.
    intro=Scene_TideboundBirdPrelude.new(nil);intro.build
    words=intro.instance_variable_get(:@words);words.opacity=255
    bird=intro.instance_variable_get(:@bird);bird.bitmap=intro.instance_variable_get(:@open_eye)
    4.times { Graphics.update }
    b=Graphics.snap_to_bitmap;b.to_file('demo-opening-caption.png');b.dispose
    File.write('DEMO_NATIVE_PASS.txt',"PASS: legacy party/inventory preserved; night/window rendering; visible Psyduck and regional level16 evolution; ordinary Psyduck unchanged; 15 sailor events; ships; blocked-save relocation; repeatable demo endpoint/save; two actual sailor wins; overworld wild win; 5 native death messages; opening caption.\n")
    puts 'DEMO_NATIVE_PASS';exit
  rescue Exception=>e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('DEMO_NATIVE_FAIL.txt',e.full_message);puts e.full_message;exit(1)
  end
end
Scene_Map.prepend(DemoNativeCheck)
