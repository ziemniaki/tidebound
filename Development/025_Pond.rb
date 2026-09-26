# Recovered source: optional pond area. Not embedded until the resume recipe runs.
GameData::EncounterType.register(id: :PondGrass, type: :land, trigger_chance: 18)
module Tidebound::Pond
  module_function
  def flags; Tidebound::Opening.flags[:pond] ||= {}; end
  def here?; $game_map && $game_map.map_id==108; end
  def water?(x,y); Tidebound::PondGeometry::WATER.include?([x,y]); end
  def say(*lines); lines.each { |line| pbMessage(line) }; end
  FISHERS={
    toma: ['Toma',[[:MAGIKARP,9],[:GOLDEEN,10]],
      "Toma: The sea takes my hooks. This pond usually gives them back. Care for a little battle while the fish ignore us?",
      "Toma: Well played. Even a quiet pond has its surprises.",
      "Toma: That duck comes here when the road gets noisy. We leave the shallow bank to it."],
    ida: ['Ida',[[:WOOPER,10],[:POLIWAG,11]],
      "Ida: I mend nets for the dock crews. This is where I rest my hands. Shall we let our companions stretch instead?",
      "Ida: A useful lesson. Thank you for taking the time.",
      "Ida: I can see marks on that stone, but I can't read them from here. And I'm certainly not swimming across."],
    renzo: ['Renzo',[[:BARBOACH,12]],
      "Renzo: Aipom stole my bait. Then it came back for the lid. Help me recover a little dignity with a battle?",
      "Renzo: There goes the dignity. At least I still have the bucket.",
      "Renzo: Someone used to prune the berry tree. I take two and leave the rest. Seems only fair."]
  }.freeze
  def fisher(id)
    name,team,invite,defeat,after=FISHERS.fetch(id)
    return say(after) if flags[id]
    return unless pbConfirmMessage(invite)
    return unless Tidebound::NeighborQuest.able?
    foe=NPCTrainer.new(name,:FISHERMAN);foe.lose_text=defeat
    team.each { |species,level| foe.party<<Pokemon.new(species,level,foe) }
    result=Tidebound.trainer!(foe)
    if result==:astral
      Tidebound::Opening.travel(105,15,21,8)
    elsif result==1
      flags[id]=true;say(defeat,after)
    end
  end
  def hidden_item
    return say('Only dry leaves remain in the little hollow.') if flags[:cache]
    say('Behind the roots, something has been wrapped in old waxed cloth.')
    flags[:cache]=true if pbReceiveItem(:MYSTICWATER)
  end
  def safe_arrival
    return unless here?
    return if flags[:revision]==1
    x=$game_player.x;y=$game_player.y
    mask=Tidebound::MAP_PASSAGES[108]
    if y>=48 && (mask[y].nil? || mask[y][x]!='1' || Tidebound::PondGeometry::ISLAND.include?([x,y]))
      $game_player.moveto(26,52)
    end
    flags[:revision]=1
  end
end
module Tidebound::PondEncounters
  def encounter_type
    type=super
    return :PondGrass if type==:Land && Tidebound::Pond.here? && $game_player.y>=48
    type
  end
end
PokemonEncounters.prepend(Tidebound::PondEncounters)
module Tidebound::PondTerrain
  def terrain_tag(x,y,count_bridge=false)
    return GameData::TerrainTag.get(:StillWater) if @map_id==108 && Tidebound::Pond.water?(x,y)
    super
  end
  def passable?(x,y,d,self_event=nil)
    if @map_id==108 && Tidebound::Pond.water?(x,y)
      return !!($PokemonGlobal && $PokemonGlobal.surfing && (self_event.nil? || self_event==$game_player))
    end
    super
  end
end
Game_Map.prepend(Tidebound::PondTerrain)
EventHandlers.add(:on_frame_update,:tidebound_pond_arrival,proc {
  Tidebound::Pond.safe_arrival if $scene.is_a?(Scene_Map) && $game_player
})
