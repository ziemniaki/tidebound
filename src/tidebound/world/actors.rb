# Features declare availability; this module owns application and indexing only.
module Tidebound::Actors
  ENTRY_RULES = {}
  FRAME_RULES = {}
  @frame_events = {}
  module_function

  def on_entry(*keys, &rule)
    keys.each do |key|
      raise "Unknown actor: #{key}" unless Tidebound::World::ACTORS.key?(key.to_sym)
      raise "Duplicate actor policy: #{key}" if ENTRY_RULES.key?(key.to_s)
      ENTRY_RULES[key.to_s] = rule
    end
  end

  def on_frame(*roles, &rule)
    roles.each do |role|
      known =
        Tidebound::World::ACTOR_SETTINGS.values.any? do |events|
          events.values.any? { |actor| actor["role"] == role }
        end
      raise "Unknown actor role: #{role}" unless known
      raise "Duplicate role policy: #{role}" if FRAME_RULES.key?(role)
      FRAME_RULES[role] = rule
    end
    @frame_events.clear
  end

  def info(event)
    Tidebound::World::ACTOR_SETTINGS.dig(event.map_id, event.id) || {}
  end

  def role(event)
    info(event)["role"]
  end

  def visible?(event, actor = info(event))
    rule = ENTRY_RULES[actor["key"]] || FRAME_RULES[actor["role"]]
    rule ? !!rule.call(event, actor) : true
  end

  def available?(event)
    event && !event.move_route_forcing && !Tidebound::Scenes.owns?(event)
  end

  def sync(map)
    events =
      @frame_events[map.map_id] ||= Tidebound::World::ACTOR_SETTINGS
        .fetch(map.map_id, {})
        .select { |_id, actor| FRAME_RULES.key?(actor["role"]) }
    events.each do |id, actor|
      event = map.events[id]
      event.through = !visible?(event, actor) if available?(event)
    end
  end

  def refresh(map)
    Tidebound::World::ACTOR_SETTINGS
      .fetch(map.map_id, {})
      .each do |id, actor|
        next unless ENTRY_RULES.key?(actor["key"])
        event = map.events[id]
        next unless available?(event)
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
  proc { |_previous| Tidebound::Actors.refresh($game_map) }
)
