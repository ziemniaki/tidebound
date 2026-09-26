# TEST ONLY, injected into a disposable Linux engine. Release archive excludes it.
$stdout.sync=true
module InteriorInput
  def trigger?(key)
    return !!($game_temp && $game_temp.message_window_showing && Graphics.frame_count%5==0) if key==Input::USE
    super
  end
end
Input.singleton_class.prepend(InteriorInput)
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('chosen-party.rxdata'))
  end
end
EventHandlers.add(:on_frame_update,:interior_meal_shot,proc {
  if Tidebound::NeighborQuest.meal_visible && !$interior_meal_shot
    b=Graphics.snap_to_bitmap;b.to_file('interior-meal.png');b.dispose;$interior_meal_shot=true
  end
})
module InteriorCheck
  def shot(name)
    18.times {Graphics.update;updateSpritesets}
    b=Graphics.snap_to_bitmap;b.to_file("interior-#{name}.png");b.dispose
    puts "SHOT #{name}"
  end
  def step(dir)
    12.times {Graphics.update;Input.update;update}
    old=[$game_map.map_id,$game_player.x,$game_player.y]
    $game_player.public_send("move_#{dir}")
    28.times {Graphics.update;Input.update;update}
    raise "blocked #{dir} from #{old}" if old==[$game_map.map_id,$game_player.x,$game_player.y]
  end
  def update
    super
    return if @interior_checked || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @interior_checked=true
    o=Tidebound::Opening;n=Tidebound::NeighborQuest;v=Tidebound::VaultVisit
    original=Tidebound.identity($player.party.first)
    # Reconstruct the pre-choice household for geometry/animation only.
    pets=o.household_pets.dup
    o.household_pets[:MAKUHITA]=Pokemon.new(:MAKUHITA,7)
    o.flags[:bedroom_talk]=false;o.flags[:walk_state]=:not_started
    o.travel(107,6,8);shot('bedroom');o.bedroom_pet
    raise 'bedroom talk' unless o.flags[:bedroom_talk] && o.actor('Mother visiting').y==11
    o.flags[:hall_talk]=false;$game_player.moveto(8,11);step('down')
    raise "bedroom stair/hall scene: #{$game_map.map_id}, #{$game_player.x}, #{$game_player.y}, #{o.flags[:hall_talk]}" unless $game_map.map_id==101 && o.flags[:hall_talk]
    raise 'Maku/crate staging' unless o.actor('House:MAKUHITA').y==10 && o.actor('Crate').x==11
    o.flags[:walk_state]=:complete;shot('living-room')
    o.travel(101,6,4);step('up');raise 'up bedroom stair' unless $game_map.map_id==107
    $game_player.moveto(8,11);step('down');raise 'down bedroom stair' unless $game_map.map_id==101
    o.travel(101,17,4);step('up');raise "up lantern stair: #{$game_map.map_id}, #{$game_player.x}, #{$game_player.y}" unless $game_map.map_id==104
    o.flags[:lamp_lit]=false;shot('lantern-unlit')
    o.flags[:oil_returned]=true;o.main_lamp;shot('lantern-lit')
    raise 'lamp flag' unless o.flags[:lamp_lit]
    $game_player.moveto(6,10);step('down');raise 'down lantern stair' unless $game_map.map_id==101
    # Real meal scene retains table coordinates and pet route.
    o.household_pets.replace(pets);n.q[:stage]=:pie;$bag.add(n::PIE)
    o.travel(101,12,8);n.meal
    raise 'meal/plate' unless n.stage==:plate && $bag.has?(n::PLATE) && $interior_meal_shot
    n.q[:stage]=:complete;v.q[:gift]=true;v.q[:open]=false;v.q[:talk]=false
    o.travel(101,12,8);v.mother
    raise 'Mother route' unless v.q[:open] && o.actor('Mother').x==3 && o.actor('Mother').y==11
    $game_player.moveto(4,12);step('left');raise 'cellar stair' unless $game_map.map_id==110
    $game_player.moveto(12,10);shot('cellar')
    $game_player.moveto(6,13);step('down');raise 'cellar return' unless $game_map.map_id==101
    step('left');raise 'cellar reentry' unless $game_map.map_id==110
    o.travel(110,17,5);v.vault_door
    12.times {Graphics.update;Input.update;update}
    raise 'vault conversation' unless v.q[:talk] && $game_player.y==10
    shot('vault');$game_player.moveto(12,17);step('down')
    raise 'vault return' unless $game_map.map_id==110
    # Old saves on now-solid furniture are relocated, not reset.
    [[107,3,5],[101,8,7],[104,6,4],[110,10,4],[111,4,3]].each do |id,x,y|
      o.travel(id,x,y);o.flags[:landscape_revisions].delete(id)
      Tidebound::Landscape.safe_arrival
      raise "unsafe old save #{id}" unless Tidebound::MAP_PASSAGES[id][$game_player.y][$game_player.x]=='1'
    end
    raise 'changed companion' unless Tidebound.identity($player.party.first)==original
    raise 'save failed' unless Game.save('interior-progress.rxdata')
    File.write('INTERIORS_PASS.txt','PASS: bedroom and hall native scenes; Maku/crate paths; every stair pair; real pie meal; lamp off/on; Mother cellar departure; vault dialogue and exit; five blocked old-save positions; unchanged companion identity; native save.')
    exit
  rescue Exception=>e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('INTERIORS_FAIL.txt',e.full_message);puts e.full_message;exit(1)
  end
end
Scene_Map.prepend(InteriorCheck)
