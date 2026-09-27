# Roles are authored beside events; display labels never select gameplay policy.
module Tidebound::Actors
  COMPANION_ROLES = %w[spirit house room outside_dog wood_bird neighbor_wild shore_duck].freeze
  SCENE_KEYS = %w[
    seller_outside
    mother_visiting
    road_thief
    running_thief
    robbery_youth_one
    robbery_youth_two
    mother
    seller_at_home
    oil_seller
    mother_at_vault
    seller_at_vault
  ].freeze
  # Index authored policies once. Map updates visit only actors whose collision can change.
  COLLISION_ACTORS =
    Tidebound::World::ACTOR_SETTINGS
      .transform_values do |events|
        events.select { |_id, actor| (COMPANION_ROLES + %w[keys crate]).include?(actor["role"]) }
      end
      .freeze
  SCENE_ACTORS =
    Tidebound::World::ACTOR_SETTINGS
      .transform_values do |events|
        events.select { |_id, actor| SCENE_KEYS.include?(actor["key"]) }
      end
      .freeze
  module_function

  def info(event)
    Tidebound::World::ACTOR_SETTINGS.dig(event.map_id, event.id) || {}
  end

  def role(event)
    info(event)["role"]
  end

  def companion?(event)
    COMPANION_ROLES.include?(role(event))
  end

  def visible?(event, actor = info(event))
    case actor["key"]
    when "seller_outside"
      return !Tidebound.story[:shop_unlocked]
    when "mother_visiting", "running_thief", "robbery_youth_one", "robbery_youth_two"
      return false
    when "road_thief"
      return Tidebound::NeighborQuest.stage == :pursuit && !Tidebound::NeighborQuest.q[:first_won]
    when "mother"
      return !Tidebound::VaultVisit.q[:open] || !!Tidebound::VaultVisit.q[:museum]
    when "seller_at_home"
      return !!Tidebound::VaultVisit.q[:gift] && !Tidebound::VaultVisit.q[:open]
    when "oil_seller"
      return !Tidebound::VaultVisit.q[:gift] || !!Tidebound::VaultVisit.q[:museum]
    when "mother_at_vault", "seller_at_vault"
      return !!Tidebound::VaultVisit.q[:open] && !Tidebound::VaultVisit.q[:museum]
    end
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
    COLLISION_ACTORS
      .fetch(map.map_id, {})
      .each do |id, actor|
        event = map.events[id]
        next unless event && !event.move_route_forcing && !Tidebound::Scenes.owns?(event)
        event.through = !visible?(event, actor)
      end
  end

  # Scene actors can move or appear temporarily during dialogue. Apply their resting
  # state only on entry or an explicit scene boundary, never on every frame.
  def refresh(map)
    SCENE_ACTORS
      .fetch(map.map_id, {})
      .each do |id, actor|
        event = map.events[id]
        next unless event && !event.move_route_forcing && !Tidebound::Scenes.owns?(event)
        visible = visible?(event, actor)
        event.opacity = visible ? 255 : 0
        event.through = !visible
      end
    sync(map)
  end
end

module Tidebound::ActorMapUpdate
  def update(*args)
    super
    Tidebound::Actors.sync(self)
  end
end
Game_Map.prepend(Tidebound::ActorMapUpdate)

EventHandlers.add(
  :on_enter_map,
  :tidebound_actor_state,
  proc { |_previous_map| Tidebound::Actors.refresh($game_map) }
)
