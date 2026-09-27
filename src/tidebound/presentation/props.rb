# Static world art uses explicit anchors; map events retain interaction and collision.
class TideboundWorldProp < Tidebound::Presentation::OwnedSprite
  def initialize(event, viewport)
    super(viewport)
    @event = event
    info = Tidebound::Actors.info(event)
    name = info["asset"] || info.fetch("role")
    @layer = Tidebound::Presentation::PROP_ASSETS.fetch(name)["z"]
    load_prop(name)
    update
  end

  def update
    super
    position_at_event(@event)
    self.z = @layer unless @layer.nil?
  end
end

EventHandlers.add(
  :on_new_spriteset_map,
  :tidebound_static_props,
  proc do |spriteset, viewport|
    next unless Tidebound::World::MAP_IDS.include?(spriteset.map.map_id)
    spriteset.map.events.each_value do |event|
      role = Tidebound::Actors.role(event)
      next unless %w[prop coast_lamp].include?(role)
      spriteset.addUserSprite(TideboundWorldProp.new(event, viewport))
    end
  end
)
