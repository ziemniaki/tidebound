# TEST ONLY. Loads a retained old save into a disposable engine directory.
module FieldInput
  def trigger?(key)
    return Graphics.frame_count%6==0 if key==Input::USE
    super
  end
end
Input.singleton_class.prepend(FieldInput)
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('chosen-party.rxdata'))
  end
end
module FieldView
  def shot(name)
    12.times { Graphics.update; updateSpritesets }
    b=Graphics.snap_to_bitmap;b.to_file("vault-#{name}.png");b.dispose
  end
  def update
    super
    return if @fields_checked || !$player || !$game_map || pbMapInterpreterRunning? || $game_temp.message_window_showing
    @fields_checked=true
    o=Tidebound::Opening;v=Tidebound::VaultVisit;n=Tidebound::NeighborQuest
    id=Tidebound.identity($player.party.first)
    n.q[:stage]=:complete
    Tidebound::World.travel(:shop,8,8);Tidebound::Interactions.oil_seller
    raise 'gift/departure' unless v.q[:gift] && $bag.quantity(v::GIFT)==1 && $game_map.map_id==102
    Tidebound::World.travel(:shop,8,10);raise 'seller duplicate' unless Tidebound::World.actor(:oil_seller).opacity==0
    Tidebound::World.travel(:home,12,8);shot('hall')
    raise 'seller home' unless Tidebound::World.actor(:seller_at_home).opacity==255
    Tidebound::Interactions.mother
    raise 'stairs or mother duplicate' unless v.q[:open] && Tidebound::World.actor(:mother).opacity==0
    v.stairs;shot('cellar');v.vault_door
    10.times { update;Graphics.update };shot('vault')
    raise 'dialogue' unless v.q[:talk]
    raise 'mother vault' unless Tidebound::World.actor(:mother_at_vault).opacity==255
    save=SaveData.compile_save_hash;File.binwrite('vault-progress.rxdata',Marshal.dump(save))
    raise 'save' unless Marshal.load(File.binread('vault-progress.rxdata'))[:tidebound].story[:vault_visit][:talk]
    Tidebound::World.travel(:road,42,43);v.city_gate;shot('docks')
    raise 'docks/night' unless $game_map.map_id==112 && $game_screen.tone.red==-80
    Tidebound::World.travel(:docks,32,23);shot('museum-front');Tidebound::World.travel(:museum,14,18);shot('museum')
    Tidebound::World.travel(:museum,15,9);v.sabre;shot('sabre')
    raise 'museum' unless v.q[:museum]
    Tidebound::World.travel(:home,12,8);raise 'mother return' unless Tidebound::World.actor(:mother).opacity==255
    Tidebound::World.travel(:shop,8,8);raise 'seller return' unless Tidebound::World.actor(:oil_seller).opacity==255
    Tidebound::Interactions.oil_seller
    raise 'duplicate gift' unless $bag.quantity(v::GIFT)==1
    raise 'pet identity' unless Tidebound.identity($player.party.first)==id
    File.write('VAULT_PASS.txt','PASS: saved companion, gift/departure, NPC exclusivity, stairs/vault dialogue, persisted state, docks/night/museum/sabre, NPC return, no duplicate reward.')
    exit
  rescue Exception=>e
    raise if e.is_a?(SystemExit) && e.status==0
    File.write('VAULT_FAIL.txt',e.full_message);exit(1)
  end
end
Scene_Map.prepend(FieldView)
