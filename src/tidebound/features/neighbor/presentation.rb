# Household props switch approved images when story state changes.
class TideboundMealProp < Tidebound::Presentation::OwnedSprite
  def initialize(viewport)
    super(viewport)
    @eaten = :uninitialized
    update
  end
  def update
    super
    q = Tidebound::NeighborQuest
    self.visible = !!q.meal_visible && $game_map.map_id == 101
    if @eaten != q.meal_eaten
      @eaten = q.meal_eaten
      load_prop(@eaten ? "plate" : "pie")
    end
    position_at_tile($game_map, 9, 8, dx: 8)
    self.z = 150
  end
end
class TideboundPearlProp < Tidebound::Presentation::OwnedSprite
  def initialize(event, viewport)
    super(viewport)
    @event = event
    load_prop("pearl")
    update
  end
  def update
    super
    q = Tidebound::NeighborQuest
    self.visible = !!q.pearl_visible
    position_at_event(@event, dy: -14, dz: 1)
    self.opacity = 190
    v = (28 * q.pearl_glint.to_f).to_i
    self.bitmap.fill_rect(12, 10, 2, 2, Color.new(206 + v, 211 + v, 201 + v))
  end
end
EventHandlers.add(
  :on_new_spriteset_map,
  :tidebound_neighbor_props,
  proc do |s, v|
    if s.map.map_id == 101
      s.addUserSprite(TideboundMealProp.new(v))
    elsif s.map.map_id == 106
      e = s.map.events[Tidebound::World::ACTORS.fetch(:oil_seller).fetch("event")]
      s.addUserSprite(TideboundPearlProp.new(e, v)) if e
    end
  end
)
