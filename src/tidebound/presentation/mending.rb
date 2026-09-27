class Scene_TideboundMending
  attr_reader :game
  def initialize
    @game = Tidebound::Mending::Game.new
    @sprites = []
    @bitmaps = []
    @time = 0.0
    @next_move = 0.0
    @grace = 0.0
    @caption = "Find three stitches. Let them sleep."
  end
  def bitmap(w, h)
    b = Bitmap.new(w, h)
    @bitmaps << b
    b
  end
  def sprite(b, z)
    s = Sprite.new(@viewport)
    s.bitmap = b
    s.z = z
    @sprites << s
    s
  end
  def ink(b, x, y, w, h, r, g, blue, a = 255)
    b.fill_rect(x, y, w, h, Color.new(r, g, blue, a))
  end
  def oval(b, x, y, rx, ry, col)
    (-ry..ry).each do |dy|
      dx = (rx * Math.sqrt([1 - (dy.to_f / ry)**2, 0].max)).to_i
      b.fill_rect(x - dx, y + dy, dx * 2 + 1, 1, col)
    end
  end
  def line(b, x, y, xx, yy, col)
    steps = [(xx - x).abs, (yy - y).abs, 1].max
    (0..steps).each do |n|
      b.fill_rect(x + (xx - x) * n / steps, y + (yy - y) * n / steps, 1, 1, col)
    end
  end
  def point(cell)
    [33 + cell[0] * 10, 39 + cell[1] * 10]
  end
  def main
    build
    @last = System.uptime
    pbBGMPlay("Tidebound Stillness", 80, 70)
    Graphics.transition(20)
    loop do
      Graphics.update
      Input.update
      now = System.uptime
      dt = [[now - @last, 0.001].max, 0.1].min
      @last = now
      result = update(dt)
      return result unless result.nil?
    end
  ensure
    dispose
  end
  def dispose
    @sprites.reverse_each { |s| s.dispose unless s.disposed? }
    @bitmaps.reverse_each { |b| b.dispose unless b.disposed? }
    @viewport.dispose if @viewport && !@viewport.disposed?
  end
  def build
    @viewport = Viewport.new(0, 0, Graphics.width, Graphics.height)
    @viewport.z = 100_000
    back = bitmap(256, 192)
    ink(back, 0, 0, 256, 192, 7, 8, 12)
    # A vast opened body: familiar Chansey outline, stretched egg-pouch/ribs,
    # bone seams and suspended Pokemon shapes. Pixel geometry, no stock gore.
    skin = Color.new(111, 70, 78)
    pale = Color.new(166, 128, 127)
    dark = Color.new(38, 21, 32)
    oval(back, 128, 89, 106, 78, dark)
    oval(back, 128, 89, 96, 73, skin)
    # Sagging, asymmetric skin lobes interrupt the recognisable egg silhouette.
    [
      [42, 88, 15, 33],
      [207, 102, 17, 28],
      [78, 41, 24, 19],
      [172, 52, 31, 19]
    ].each { |x, y, rx, ry| oval(back, x, y, rx, ry, Color.new(122, 77, 82)) }
    oval(back, 128, 101, 78, 56, Color.new(46, 23, 34))
    # Torn abdominal lips, pale connective tissue and exposed vertebrae.
    12.times do |i|
      y = 53 + i * 9
      spread = (Math.sqrt([1 - ((y - 104) / 58.0)**2, 0].max) * 76).to_i
      [-1, 1].each do |side|
        x = 128 + side * spread
        oval(back, x, y, 4, 7, Color.new(171, 102, 104))
        line(back, x, y - 3, x - side * 6, y + 5, Color.new(206, 162, 147))
        line(back, x + side * 3, y, x + side * 9, y + 5, Color.new(69, 26, 42))
      end
    end
    9.times do |i|
      y = 57 + i * 10
      ink(back, 119, y, 7, 4, 155, 128, 117)
      ink(back, 117, y + 1, 3, 2, 188, 160, 141)
      ink(back, 126, y + 2, 3, 2, 83, 48, 60)
    end
    [-1, 1].each do |side|
      5.times do |n|
        x = 128 + side * (86 + n * 2)
        y = 45 + n * 12
        line(back, x, y, x + side * 17, y - 10, pale)
        line(back, x, y + 2, x + side * 13, y - 3, skin)
      end
      7.times do |n|
        y = 58 + n * 12
        3.times do |thick|
          line(back, 128 + side * 72, y + thick, 128 + side * 47, y + 10 + thick, pale)
          line(
            back,
            128 + side * 47,
            y + 10 + thick,
            128 + side * 22,
            y + 12 + thick,
            Color.new(126, 95, 97)
          )
        end
        line(back, 128 + side * 24, y + 12, 128 + side * 27, y + 18, Color.new(176, 98, 109))
      end
      ey = side < 0 ? 28 : 34
      oval(back, 128 + side * 22, ey, 8, 4, Color.new(43, 24, 34))
      ink(back, 122 + side * 22, ey, 11, 1, 202, 167, 148)
      ink(back, 128 + side * 22, ey, 1, 2, 239, 215, 170)
      line(back, 128 + side * 22, ey + 4, 125 + side * 22, ey + 12, Color.new(65, 32, 47))
    end
    oval(back, 123, 44, 12, 8, Color.new(16, 17, 23))
    5.times { |i| ink(back, 114 + i * 4, 39, 2, 5, 196, 179, 156) }
    # A long sutured facial tear: it cannot settle into a friendly smile.
    line(back, 111, 17, 154, 45, Color.new(41, 25, 37))
    6.times do |i|
      line(back, 112 + i * 7, 14 + i * 5, 109 + i * 7, 22 + i * 5, Color.new(196, 174, 149))
    end
    # Egg membrane, severed loops and dark drips remain in the non-walkable space.
    14.times do |n|
      x = 42 + (n * 37) % 174
      y = 54 + (n * 17) % 106
      oval(back, x, y, 4, 7, Color.new(81, 40, 55))
      line(back, x, y, x - 3, y + 10, Color.new(144, 66, 76))
    end
    # Looped tissue at the cavity's lower edge; slow animation stays in the nests.
    5.times do |i|
      oval(back, 78 + i * 22, 152 - (i % 2) * 4, 13, 6, Color.new(104, 48, 66))
      oval(back, 78 + i * 22, 152 - (i % 2) * 4, 9, 3, Color.new(31, 21, 32))
      line(
        back,
        72 + i * 22,
        147 - (i % 2) * 4,
        81 + i * 22,
        147 - (i % 2) * 4,
        Color.new(165, 94, 105)
      )
    end
    Tidebound::Mending::CELLS.each_key do |c|
      x, y = point(c)
      ink(back, x - 4, y - 4, 9, 9, 32, 38, 41)
      ink(back, x - 3, y + 3, 7, 1, 123, 108, 99)
    end
    @body = sprite(back, 0)
    @body.zoom_x = @body.zoom_y = 2
    live = bitmap(256, 192)
    @live = sprite(live, 2)
    @live.zoom_x = @live.zoom_y = 2
    @icons = Bitmap.new("Graphics/Pokemon/Icons/NATU")
    @bitmaps << @icons
    @hud_state = nil
    @hud_background = bitmap(Graphics.width, Graphics.height)
    pbSetSystemFont(@hud_background)
    @hud_background.fill_rect(0, 0, Graphics.width, 42, Color.new(7, 8, 12, 245))
    @hud_background.fill_rect(0, 320, Graphics.width, 64, Color.new(7, 8, 12, 245))
    @hud_background.font.size = 17
    @hud_background.font.color = Color.new(158, 172, 165)
    @hud_background.draw_text(
      4,
      352,
      Graphics.width - 8,
      28,
      "Arrows: walk   Enter: loosen stitch   Esc: leave",
      1
    )
    @text = bitmap(Graphics.width, Graphics.height)
    sprite(@text, 5)
    pbSetSystemFont(@text)
    @veil = sprite(bitmap(Graphics.width, Graphics.height), 6)
    @veil.bitmap.fill_rect(0, 0, Graphics.width, Graphics.height, Color.new(6, 9, 14))
    @veil.opacity = 255
    @title = bitmap(Graphics.width, Graphics.height)
    sprite(@title, 7)
    pbSetSystemFont(@title)
    @title.font.color = Color.new(206, 202, 178)
    @title.font.size = 26
    @title.draw_text(0, 125, Graphics.width, 40, "PET HOUSE", 1)
    @title.font.size = 20
    @title.draw_text(0, 175, Graphics.width, 32, "Bring everyone home.", 1)
    draw
  end
  def update(dt)
    @time += dt
    if @time < 3
      @veil.opacity = 255
      return nil
    end
    @title.clear unless @title_cleared
    @title_cleared = true
    @veil.opacity = [255 - ((@time - 3) * 150).to_i, 0].max
    return nil if @time < 4.8
    if @finish_time
      @caption = "They are light enough to carry now."
      draw
      return true if @time - @finish_time > 2.3
      return nil
    end
    return false if Input.trigger?(Input::BACK)
    if @time >= @next_move
      d = { 2 => [0, 1], 4 => [-1, 0], 6 => [1, 0], 8 => [0, -1] }[Input.dir4]
      @next_move = @time + 0.14 if d && @game.move(*d)
    end
    if Input.trigger?(Input::USE)
      i = @game.loosen
      unless i.nil?
        @caption =
          [
            "Under the skin: a bird, still trying to sing.",
            "The second mouth finally stops breathing.",
            "It remembered RETURN. Nobody came."
          ][
            i
          ]
        @caption_until = @time + 4
      end
    end
    # Two slow contractions; several alternate routes and all freed nests persist.
    hazard = [9, 6 + (Math.sin(@time * 0.75) > 0 ? 0 : 1)]
    if @game.cell == hazard && @time > @grace
      @game.bump
      @grace = @time + 2
      @caption = "The body swallows. The loose stitches stay loose."
      @caption_until = @time + 3
    end
    @caption =
      (
        if @game.freed.length == 3
          "The mouth is open. Go north."
        else
          "Find three stitches. Let them sleep."
        end
      ) if @caption_until && @time > @caption_until
    @finish_time = @time if @game.won?
    draw
    nil
  end
  def draw
    b = @live.bitmap
    b.clear
    pulse = (Math.sin(@time * 1.5) * 2).to_i
    Tidebound::Mending::NESTS.each_with_index do |c, i|
      x, y = point(c)
      if @game.freed.include?(i)
        oval(b, x, y, 6, 4, Color.new(15, 21, 26))
        ink(b, x - 3, y, 6, 1, 151, 188, 170)
        next
      end
      oval(b, x, y, 11, 12 + pulse, Color.new(60, 32, 46))
      oval(b, x, y, 8, 10, Color.new(154, 91, 99))
      # Tiny native Natu silhouette embedded in an opened sac, held by sutures.
      b.stretch_blt(Rect.new(x - 12, y - 13, 24, 24), @icons, Rect.new(0, 0, 64, 64))
      [-5, 0, 5].each do |off|
        line(b, x - 8, y + off, x + 8, y + off + 2, Color.new(222, 200, 168))
        ink(b, x - 8, y + off, 2, 3, 49, 27, 37)
        ink(b, x + 8, y + off + 2, 2, 3, 49, 27, 37)
      end
    end
    x, y = point([9, 6 + (Math.sin(@time * 0.75) > 0 ? 0 : 1)])
    oval(b, x, y, 5, 3 + pulse.abs, Color.new(161, 84, 99))
    ink(b, x - 4, y, 8, 1, 233, 181, 162)
    x, y = point(@game.cell)
    oval(b, x, y + 2, 4, 2, Color.new(8, 15, 21))
    ink(b, x - 2, y - 4, 5, 6, 205, 214, 192)
    ink(b, x + 1, y - 3, 1, 2, 35, 41, 43)
    ink(b, x - 1, y + 2, 1, 2, 173, 148, 105)
    if @game.freed.length == 3
      x, y = point(Tidebound::Mending::EXIT)
      ink(b, x - 3, y - 4, 7, 8, 163, 194, 176)
    end
    draw_hud
  end
  def draw_hud
    state = [@game.freed.length, @caption]
    return if @hud_state == state
    @hud_state = state
    # Native font glyphs can extend beyond draw_text's rectangle. Restore the
    # complete static layer so a shorter caption cannot leave old pixels behind.
    @text.clear
    @text.blt(0, 0, @hud_background, Rect.new(0, 0, Graphics.width, Graphics.height))
    @text.font.size = 22
    @text.font.color = Color.new(216, 201, 182)
    @text.draw_text(12, 4, Graphics.width - 24, 32, "THE MENDING     #{@game.freed.length} / 3", 1)
    @text.font.size = 17
    @text.draw_text(4, 321, Graphics.width - 8, 30, @caption, 1)
  end
end
