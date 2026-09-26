# Current actor policy is independent of sprite allocation and drawing.
module Tidebound::Actors
  module_function

  def companion?(event)
    event.name.match?(/\A(?:Spirit:|Wild:|House:|Room:|Pookie outside\z)/)
  end

  def visible?(event)
    name = event.name
    if name.start_with?("Spirit:")
      soul = Tidebound.state.souls[name.split(":").last.to_i]
      return !!(soul && soul.status == :waiting && Tidebound.state.realm == :astral)
    end
    if name.match?(/\A(?:House:|Room:)/) || name == "Pookie outside"
      species = name == "Pookie outside" ? :POOCHYENA : name.split(":").last.to_sym
      return false unless (Tidebound.story[:household_pets] || {})[species]
      walk = Tidebound.story[:walk_state]
      return %i[not_started requested running at_pier].include?(walk) if name == "Pookie outside"
      if name == "Room:NATU"
        return false if walk == :complete
        return Tidebound::DreamRoom.wick_visible? if event.map_id == 115
      elsif species != :MAKUHITA
        return walk == :complete
      end
      return true
    end
    if name.start_with?("Wild:")
      return !Tidebound::Pond.flags[:shoreduck_gone] if name.end_with?(":shoreduck")
      return Tidebound::NeighborQuest.wild_visible?(name) if name.count(":") > 1
      return !Tidebound.story[:wood_bird_gone]
    end
    if name == "Shop keys"
      return !Tidebound.story[:keys_collected] && !Tidebound.story[:shop_unlocked]
    end
    true
  end

  def sync(map)
    return unless Tidebound::World::MAP_IDS.include?(map.map_id)
    map.events.each_value do |event|
      next if event.move_route_forcing
      if companion?(event) || event.name == "Shop keys" || event.name.start_with?("Crate")
        event.through = !visible?(event)
      end
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
