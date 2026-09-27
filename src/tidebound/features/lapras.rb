# The opening pier apparition and its transient presentation state.
module Tidebound::SeaGlimpse
  class << self
    attr_accessor :visible, :alpha
  end
  module_function
  def play
    pbMessage("The rope draws tight.\nThere is no boat at the end of it.")
    pbBGMFade(0.5)
    Tidebound::World.camera_to(*Tidebound::World.coast_xy(55, 22))
    pbWait(0.65)
    self.alpha = 0
    self.visible = true
    pbWait(0.9) { |elapsed| self.alpha = (145 * [elapsed / 0.9, 1.0].min).to_i }
    self.alpha = 145
    pbMessage("Something pale rises through the dark water.")
    pbMessage("A face. Turned towards the lighthouse, as if waiting for its light.")
    pbWait(0.65)
    pbMessage("The sea goes on behind it. Farther than you can see.")
    pbWait(1.0) { |elapsed| self.alpha = (145 * [1.0 - elapsed, 0].max).to_i }
    self.visible = false
    pbWait(0.4)
    Tidebound.story[:lapras_glimpsed] = true
    pbMessage("Only the rope is moving now.")
  ensure
    self.visible = false
    self.alpha = 0
    Tidebound::World.camera_home if $game_map.map_id == 102
    pbBGMPlay("Tidebound Shore", 80, 100)
  end
end
