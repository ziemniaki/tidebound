# Code-drawn household props in the same style as the existing lamps/crates.
class TideboundMealProp < Tidebound::Presentation::OwnedSprite
  def initialize(viewport)
    super(viewport)
    self.bitmap = Bitmap.new(32, 20)
    self.ox = 16
    self.oy = 10
    @eaten = nil
    update
  end
  def update
    super
    q = Tidebound::NeighborQuest
    self.visible = !!q.meal_visible && $game_map.map_id == 101
    if @eaten != q.meal_eaten
      @eaten = q.meal_eaten
      b = self.bitmap
      b.clear
      b.fill_rect(4, 4, 24, 12, Color.new(128, 134, 147))
      b.fill_rect(2, 6, 28, 8, Color.new(194, 194, 183))
      b.fill_rect(6, 2, 20, 14, Color.new(216, 211, 190))
      [8, 12].each do |x|
        b.fill_rect(x, 3, 2, 5, Color.new(63, 87, 117))
        b.fill_rect(x + 2, 2, 2, 2, Color.new(63, 87, 117))
      end
      unless @eaten
        b.fill_rect(8, 7, 16, 7, Color.new(145, 101, 68))
        b.fill_rect(10, 6, 12, 6, Color.new(183, 139, 83))
        [12, 18].each { |x| b.fill_rect(x, 8, 2, 2, Color.new(112, 77, 58)) }
      end
    end
    position_at_tile($game_map, 9, 8, dx: 8)
    self.z = 150
  end
end
class TideboundPearlProp < Tidebound::Presentation::OwnedSprite
  def initialize(event, viewport)
    super(viewport)
    @event = event
    self.bitmap = Bitmap.new(24, 16)
    [[2, 4], [4, 8], [8, 10], [12, 10], [16, 8], [18, 4]].each do |x, y|
      self.bitmap.fill_rect(x, y, 4, 4, Color.new(176, 185, 184))
      self.bitmap.fill_rect(x, y, 2, 2, Color.new(206, 211, 201))
    end
    self.ox = 12
    self.oy = 16
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
