# Small field improvements. Additive state; no save-schema or pet-identity changes.
module Tidebound::FieldDetails
  FIRE_SECONDS = 15 * 60
  BERRY_SECONDS = 60 * 60
  module_function

  def remaining(key, now = Time.now.to_i)
    last = (Tidebound.state.story[:fire_rests] || {})[key]
    return 0 unless last
    [[FIRE_SECONDS - (now - last), 0].max, FIRE_SECONDS].min
  end

  def healable_party
    $player.party.reject { |p| p.egg? || Tidebound.borrowed?(p) }
  end

  def heal_fire(key, now = Time.now.to_i)
    unless Tidebound.state.realm == :living
      raise Tidebound::TransitionError, "Fire belongs to the living world"
    end
    return false if remaining(key, now) > 0
    party = healable_party
    return false if party.empty?
    party.each do |p|
      p.hp = p.totalhp
      p.moves.each { |move| move.pp = move.total_pp }
    end
    (Tidebound.state.story[:fire_rests] ||= {})[key] = now
    true
  end

  def rest(key, checkpoint)
    Tidebound.state.checkpoint = checkpoint
    if heal_fire(key)
      pbMessage("You settle beside the fire. Your companions recover their HP and PP.")
      pbMessage("They can recover here again in 15 minutes. Poison and other conditions remain.")
    elsif healable_party.empty?
      pbMessage("You warm your hands beside the fire.")
    else
      minutes = (remaining(key) / 60.0).ceil
      pbMessage(
        "You warm your hands. Your companions need another #{minutes} minute#{minutes == 1 ? "" : "s"} before this fire can restore them again."
      )
    end
  end

  def berry(map, x, y, item)
    key = [map, x, y]
    times = (Tidebound.state.story[:berry_picks] ||= {})
    now = Time.now.to_i
    if times[key] && now - times[key] < BERRY_SECONDS
      pbMessage("Only unripe berries remain. Let them grow a little longer.")
      return
    end
    unless pbConfirmMessage(
             "Ripe #{GameData::Item.get(item).name_plural} hang among the leaves. Pick two?"
           )
      return
    end
    times[key] = now if pbReceiveItem(item, 2)
  end
end

# The generated maps override terrain globally; restore Grass only for its visible tile.
module Tidebound::FieldTerrain
  def terrain_tag(x, y, count_bridge = false)
    if [103, 108].include?(@map_id) && valid?(x, y) && data[x, y, 1] == 391
      return GameData::TerrainTag.get(:Grass)
    end
    super
  end
end
Game_Map.prepend(Tidebound::FieldTerrain)

# Route native grass encounters (including any double encounter) through the same
# pre-cleanup loss snapshot as the explicitly visible wild Pokemon.
module Tidebound::GrassBattles
  def start(*args, can_override: false)
    if can_override && [103, 108].include?($game_map.map_id) && Tidebound.state.realm == :living
      result = Tidebound::Encounters.fight(*args)
      return result == :astral ? 2 : result
    end
    super
  end
end
WildBattle.singleton_class.prepend(Tidebound::GrassBattles)
