# The southern pond: fishing battles, water terrain and optional items.
GameData::EncounterType.register(id: :PondGrass, type: :land, trigger_chance: 18)
module Tidebound::Pond
  module_function
  def flags; Tidebound.story[:pond] ||= {}; end
  def psyduck
    return if flags[:shoreduck_gone]
    return unless pbConfirmMessage("A Psyduck watches the shallows, holding its head. Approach?")
    return unless Tidebound::Encounters.able?
    outcome=Tidebound::Encounters.fight(:PSYDUCK,8)
    flags[:shoreduck_gone]=true if [1,4].include?(outcome)
  end
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
    return unless Tidebound::Encounters.able?
    foe=Tidebound::Encounters.trainer(:FISHERMAN, name, defeat, team)
    result=Tidebound.trainer!(foe)
    if result==:astral
      Tidebound::World.travel(:astral,15,21,8)
    elsif result==1
      flags[id]=true;say(defeat,after)
    end
  end
  def hidden_item
    return say('Only dry leaves remain in the little hollow.') if flags[:cache]
    say('Behind the roots, something has been wrapped in old waxed cloth.')
    flags[:cache]=true if pbReceiveItem(:MYSTICWATER)
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
