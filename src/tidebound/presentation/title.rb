class Scene_TideboundTitle
  def main
    viewport = Viewport.new(0, 0, Graphics.width, Graphics.height)
    viewport.z = 99_999
    backdrop = Sprite.new(viewport)
    backdrop.bitmap = Bitmap.new(Graphics.width, Graphics.height)
    b = backdrop.bitmap
    b.fill_rect(0, 0, Graphics.width, Graphics.height, Color.new(12, 20, 30))
    b.fill_rect(0, 205, Graphics.width, Graphics.height - 205, Color.new(18, 34, 44))
    9.times { |i| b.fill_rect(0, 210 + i * 21, Graphics.width, 1, Color.new(24, 42, 52)) }
    b.fill_rect(368, 132, 26, 97, Color.new(31, 43, 50))
    b.fill_rect(362, 125, 38, 8, Color.new(44, 51, 55))
    b.fill_rect(371, 115, 20, 12, Color.new(232, 208, 156))
    b.fill_rect(365, 108, 32, 6, Color.new(62, 62, 59))
    pbSetSystemFont(b)
    b.font.size = 40
    b.font.color = Color.new(225, 220, 206)
    b.draw_text(42, 75, 320, 55, "TIDEBOUND")
    b.font.size = 20
    b.font.color = Color.new(159, 177, 182)
    b.draw_text(44, 129, 300, 32, "The keeper's light")
    b.font.size = 18
    b.draw_text(44, 320, 420, 32, "Press Enter")
    b.font.size = 14
    b.draw_text(44, 350, 400, 24, "Demo 1 | #{Tidebound::VERSION}  |  An unofficial fan project")
    pbBGMPlay("Tidebound Shore", 80, 100)
    Graphics.transition(20)
    loop do
      Graphics.update
      Input.update
      break if Input.trigger?(Input::USE)
    end
    Graphics.freeze
    backdrop.bitmap.dispose
    backdrop.dispose
    viewport.dispose
    $scene = Scene_DebugIntro.new
  end
end
