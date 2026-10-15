# A short native scene. It changes no party, inventory or quest state.
module Tidebound::CastawayVoyage
  module_function

  def play(returning: false)
    viewport = Viewport.new(0, 0, Graphics.width, Graphics.height)
    viewport.z = 99_999
    sprites = []
    background = Sprite.new(viewport)
    sprites << background
    background.bitmap = Bitmap.new(Graphics.width, Graphics.height)
    sea = Sprite.new(viewport)
    sprites << sea
    sea.bitmap = Bitmap.new(Graphics.width * 2, Graphics.height)
    ship = Tidebound::Presentation::OwnedSprite.new(viewport)
    sprites << ship
    ship.load_prop("offshore_ship")
    ship.zoom_x = ship.zoom_y = 0.14
    ship.ox, ship.oy = 768, 800
    ship.z = 2
    caption = Sprite.new(viewport)
    sprites << caption
    caption.bitmap = Bitmap.new(Graphics.width, Graphics.height)
    pbSetSmallFont(caption.bitmap)
    caption.z = 3
    fresh_wreck = !returning && !Tidebound::Castaway.flags[:arrived]
    phases = returning ? %i[sun night] : %i[night sun]
    phases.each do |phase|
      draw(background.bitmap, sea.bitmap, caption.bitmap, phase, returning)
      duration = fresh_wreck ? 9.0 : 4.0
      pbWait(duration) do |elapsed|
        t = [elapsed / duration, 1.0].min
        ship.x = Graphics.width * (0.25 + t * 0.5)
        ship.y = Graphics.height * 0.61 + Math.sin(elapsed * 1.8) * 3
        ship.angle = Math.sin(elapsed * 1.3) * 1.5
        sea.x = -(elapsed * 22) % Graphics.width - Graphics.width
        caption.opacity = [255, (elapsed * 150).to_i, ((duration - elapsed) * 180).to_i].min
      end
    end
    if fresh_wreck
      caption.bitmap.clear
      caption.bitmap.draw_text(
        16,
        Graphics.height - 64,
        Graphics.width - 32,
        40,
        "A reef, beneath the glare.",
        1
      )
      pbWait(1.4) do |elapsed|
        ship.x += 0.1
        ship.angle = [elapsed * 8, 7].min
      end
      viewport.color = Color.new(245, 243, 220, 230)
      pbWait(0.15)
      viewport.color = Color.new(0, 0, 0, 255)
      pbWait(0.7)
    end
  ensure
    (sprites || []).reverse_each do |sprite|
      next if sprite.disposed?
      if sprite.is_a?(Tidebound::Presentation::OwnedSprite)
        sprite.dispose
      else
        sprite.bitmap.dispose if sprite.bitmap && !sprite.bitmap.disposed?
        sprite.dispose
      end
    end
    viewport.dispose if viewport && !viewport.disposed?
  end

  def draw(background, sea, caption, phase, returning)
    day = phase == :sun
    horizon = (Graphics.height * 0.35).to_i
    background.clear
    sea.clear
    caption.clear
    background.fill_rect(
      0,
      0,
      Graphics.width,
      Graphics.height,
      day ? Color.new(98, 193, 214) : Color.new(20, 32, 48)
    )
    horizon.times do |y|
      t = y.to_f / horizon
      color =
        (
          if day
            Color.new(119 + t * 85, 202 + t * 28, 220 + t * 13)
          else
            Color.new(18 + t * 20, 27 + t * 23, 44 + t * 21)
          end
        )
      background.fill_rect(0, y, Graphics.width, 1, color)
    end
    if day
      background.fill_rect(Graphics.width - 110, 35, 24, 24, Color.new(255, 246, 200))
      background.fill_rect(Graphics.width - 114, 39, 32, 16, Color.new(255, 246, 200))
    else
      24.times do |i|
        background.fill_rect(
          (i * 83 + 17) % Graphics.width,
          (i * 37 + 11) % (horizon - 15),
          2,
          2,
          Color.new(185, 201, 202, 160)
        )
      end
    end
    background.fill_rect(
      0,
      horizon,
      Graphics.width,
      Graphics.height - horizon,
      day ? Color.new(35, 153, 164) : Color.new(28, 52, 68)
    )
    48.times do |i|
      y = horizon + 8 + (i * 29) % (Graphics.height - horizon - 10)
      x = (i * 101) % Graphics.width
      color = day ? Color.new(174, 229, 206, 120) : Color.new(127, 165, 174, 65)
      [x, x + Graphics.width].each { |sx| sea.fill_rect(sx, y, 8 + i % 19, 2, color) }
    end
    text =
      if returning
        day ? "You carry the warmth with you." : "The harbour lights, at last."
      else
        day ? "Beyond the dark water, sunlight." : "THE LITTLE PROMISE"
      end
    caption.font.color = Color.new(245, 241, 222)
    caption.draw_text(16, Graphics.height - 64, Graphics.width - 32, 40, text, 1)
  end
end
