module Tidebound::Presentation::Dream
  module_function
  # A quiet, visible fold: runes gather, the body fades/turns, then unwinds at home.
  # No full-screen flash or shake. Always restore runtime state, even on exceptions.
  def fold_to(x, y)
    player = $game_player
    old_opacity = player.opacity
    old_direction = player.direction
    viewport = Viewport.new(0, 0, Graphics.width, Graphics.height)
    viewport.z = 99_997
    bitmap = Bitmap.new("Graphics/Pictures/effects/fold_runes")
    sprite = Sprite.new(viewport)
    sprite.bitmap = bitmap
    sprite.ox = 64
    sprite.oy = 64
    2.times do |half|
      20.times do |i|
        progress = (i + 1) / 20.0
        player.opacity = (old_opacity * (half == 0 ? 1 - progress : progress)).to_i
        player.direction = [2, 4, 8, 6][(i / 5) % 4]
        sprite.x = player.screen_x
        sprite.y = player.screen_y - 16
        sprite.angle = (half == 0 ? i * 4 : 80 - i * 4)
        sprite.zoom_x = sprite.zoom_y = (half == 0 ? 1.25 - progress * 0.8 : 0.45 + progress * 0.8)
        sprite.opacity = (Math.sin(progress * Math::PI) * 190).to_i
        pbWait(0.025)
      end
      player.moveto(x, y) if half == 0
    end
  ensure
    player.opacity = old_opacity if player && old_opacity
    player.direction = old_direction if player && old_direction
    sprite&.dispose
    bitmap&.dispose
    viewport&.dispose
  end
  CURSE_PAGES = [
    [
      "W A T E R   C U R S E",
      "a leaf without a tree / a room without outside",
      "give the water a word give the word a hollow",
      "do not give it the hollow where the word was",
      "under under under the hem of the shore",
      "the cup is carrying the mouth carrying the cup",
      "you said you said you said you were asleep",
      "the ink has knees / it kneels the wrong way",
      "salt remembers a shape that has not happened",
      "turn the page before it learns your fingers",
      "///////////// hush hush hush //////////////"
    ],
    [
      "a bed a bed a b e d a b e d a b",
      "there is no water here there is no here",
      "the tide has written itself on the back of the tide",
      "seven little doors inside a single closed eye",
      "open the seventh / there were never seven",
      "a lullaby with all the mouths rubbed out",
      "WHERE IS THE SHORE WHEN THE SHORE IS WORN",
      "worn warm worm word ward water w a t e r",
      "the margin cannot hold the margin cannot hold",
      "the margin cannot hold the margin cannot hold",
      "a name turned face-down / it is still listening"
    ],
    [
      "do not read the wet part",
      "do not wet the read part / part the not / read",
      "a small bell full of hair rings without a bell",
      "the sleeve reaches out for what should be an arm",
      "give back the bottom of the bowl",
      "give back the inside of the knock",
      "give back the give back the give back the",
      "the house has swallowed its nearest house",
      "THIS IS NOT THE FIRST SIDE OF THE PAPER",
      "this is not the first side this is not the first",
      "//// before before before before before ////"
    ],
    [
      "the writing thins / something keeps writing",
      "water curse water course water cradle water",
      "if you find an ending leave it where it lies",
      "a clean dry leaf / a clean dry leaf / a clean",
      "there is nothing under your thumb but tomorrow",
      "tomorrow has no underside no underside no",
      "hush little room / let the room go home",
      "a word is missing from every missing word",
      "................................................",
      "the page is dry",
      "your hand is dry / your hand is dry / your hand"
    ]
  ].freeze
  def water_curse
    viewport = Viewport.new(0, 0, Graphics.width, Graphics.height)
    viewport.z = 100_000
    shade = Sprite.new(viewport)
    shade.bitmap = Bitmap.new(Graphics.width, Graphics.height)
    shade.bitmap.fill_rect(0, 0, Graphics.width, Graphics.height, Color.new(10, 14, 25, 240))
    sheet = Sprite.new(viewport)
    sheet.bitmap = Bitmap.new(Graphics.width + 120, Graphics.height)
    strip = Sprite.new(viewport)
    strip.bitmap = Bitmap.new(Graphics.width + 120, 20)
    footer = Sprite.new(viewport)
    footer.bitmap = Bitmap.new(Graphics.width, 40)
    footer.y = Graphics.height - 40
    pbSetSystemFont(sheet.bitmap)
    pbSetSystemFont(footer.bitmap)
    sheet.bitmap.font.size = 22
    footer.bitmap.font.size = 18
    CURSE_PAGES.each_with_index do |lines, page|
      sheet.bitmap.clear
      footer.bitmap.clear
      lines.each_with_index do |line, i|
        sheet.bitmap.font.color = Color.new(i % 3 == 0 ? 168 : 195, 180, i % 3 == 0 ? 195 : 175)
        sheet.bitmap.draw_text(10 + (i % 3) * 13, 5 + i * 28, Graphics.width + 105, 32, line)
      end
      footer.bitmap.font.color = Color.new(163, 179, 188)
      footer.bitmap.draw_text(
        16,
        4,
        Graphics.width - 32,
        30,
        "#{page + 1}/4    Confirm: turn page    Cancel: close"
      )
      strip.bitmap.clear
      strip.bitmap.blt(0, 0, sheet.bitmap, Rect.new(0, 80 + page * 28, Graphics.width + 120, 18))
      elapsed = 0
      loop do
        Graphics.update
        Input.update
        elapsed += 1
        sheet.x = elapsed % 90 < 8 ? -3 : 0
        strip.y = 80 + page * 28
        strip.x = ((elapsed / 12) % 3 - 1) * 7
        strip.opacity = 60 + (elapsed / 20 % 3) * 20
        next if elapsed < 16
        break if Input.trigger?(Input::USE)
        return if Input.trigger?(Input::BACK)
      end
    end
  ensure
    [footer, strip, sheet, shade].each do |s|
      s&.bitmap&.dispose
      s&.dispose
    end
    viewport&.dispose
    Input.update
  end
end
