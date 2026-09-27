# Roles are authored beside events; display labels never select gameplay policy.
module Tidebound::Actors
  module_function

  def info(event)
    Tidebound::World::ACTOR_SETTINGS.dig(event.map_id, event.id) || {}
  end

  def role(event)
    info(event)["role"]
  end

  def companion?(event)
    %w[spirit house room outside_dog wood_bird neighbor_wild shore_duck].include?(role(event))
  end

  def visible?(event)
    actor = info(event)
    case actor["role"]
    when "spirit"
      soul = Tidebound.state.souls[actor.fetch("index")]
      !!(soul && soul.status == :waiting && Tidebound.state.realm == :astral)
    when "house", "room", "outside_dog"
      species = actor.fetch("species").to_sym
      return false unless (Tidebound.story[:household_pets] || {})[species]
      walk = Tidebound.story[:walk_state]
      if actor["role"] == "outside_dog"
        return %i[not_started requested running at_pier].include?(walk)
      end
      if actor["role"] == "room" && species == :NATU
        return false if walk == :complete
        return Tidebound::DreamRoom.wick_visible? if event.map_id == Tidebound::World::MAPS[:dream]
      elsif species != :MAKUHITA
        return walk == :complete
      end
      true
    when "shore_duck"
      !Tidebound::Pond.flags[:shoreduck_gone]
    when "neighbor_wild"
      Tidebound::NeighborQuest.wild_visible?(actor.fetch("state").to_sym)
    when "wood_bird"
      !Tidebound.story[:wood_bird_gone]
    when "keys"
      !Tidebound.story[:keys_collected] && !Tidebound.story[:shop_unlocked]
    else
      true
    end
  end

  def sync(map)
    return unless Tidebound::World::MAP_IDS.include?(map.map_id)
    map.events.each_value do |event|
      next if event.move_route_forcing
      event.through = !visible?(event) if companion?(event) || %w[keys crate].include?(role(event))
    end
  end
end

module Tidebound::ActorMapUpdate
  def update(*args)
    super
    Tidebound::Actors.sync(self)
  end
end
Game_Map.prepend(Tidebound::ActorMapUpdate)
