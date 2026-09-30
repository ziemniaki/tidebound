# Development-only Main: inspect engine-loaded assets without entering or saving a game.
module AssetPreview
  module_function

  def run(spec, frames: nil, capture: nil)
    MessageTypes.load_default_messages if FileTest.exist?("Data/messages_core.dat")
    PluginManager.runPlugins
    Game.initialize
    SaveData.initialize_bootup_values
    Graphics.resize_screen(768, 512)
    viewport = Viewport.new(0, 0, Graphics.width, Graphics.height)
    sprites = []
    background = Sprite.new(viewport)
    background.bitmap = Bitmap.new(Graphics.width, Graphics.height)
    canvas = background.bitmap
    canvas.fill_rect(0, 0, Graphics.width, Graphics.height, Color.new(35, 43, 52))
    pbSetSystemFont(canvas)
    canvas.draw_text(20, 8, 728, 36, "#{spec.fetch("kind")}/#{spec.fetch("name")}")
    canvas.draw_text(20, 468, 728, 36, "Esc: close    Enter: replay sound")
    characters = []
    kind = spec.fetch("kind")
    if kind == "pokemon"
      species, form = spec.fetch("species").to_sym, spec.fetch("form")
      [false, true].each_with_index do |shiny, group|
        [false, true].each_with_index do |back, column|
          x = 96 + (group * 2 + column) * 192
          label = "#{shiny ? "Shiny" : "Normal"} #{back ? "back" : "front"}"
          canvas.draw_text(x - 85, 58, 180, 32, label)
          sprite = PokemonSprite.new(viewport)
          sprite.setSpeciesBitmap(species, 0, form, shiny, false, back)
          sprite.x, sprite.y = x, 190
          sprites << sprite
        end
        icon = PokemonSpeciesIconSprite.new(species, viewport)
        icon.form, icon.shiny = form, shiny
        icon.x, icon.y = 192 + group * 384, 345
        sprites << icon
      end
      sound = proc { GameData::Species.play_cry_from_species(species, form) }
    elsif kind == "audio"
      category, name = spec.fetch("name").split("/", 2)
      playback = {
        "BGM" => :pbBGMPlay,
        "BGS" => :pbBGSPlay,
        "ME" => :pbMEPlay,
        "SE" => :pbSEPlay
      }.fetch(category)
      sound = proc { send(playback, name, 80, 100) }
      canvas.draw_text(20, 200, 728, 64, "#{category}: #{name}")
    else
      path = spec.fetch("path")
      if %w[items trainers].include?(kind)
        actual =
          (
            if kind == "items"
              GameData::Item.icon_filename(spec.fetch("name").to_sym)
            else
              GameData::TrainerType.front_sprite_filename(spec.fetch("name").to_sym)
            end
          )
        unless pbResolveBitmap(actual) == path
          raise "Asset fell back: #{actual.inspect}, expected #{path}"
        end
      end
      if kind == "characters"
        sheet = Bitmap.new(path)
        width, height = sheet.width / 4, sheet.height / 4
        4.times do |direction|
          sprite = Sprite.new(viewport)
          sprite.bitmap = sheet
          sprite.src_rect.set(0, direction * height, width, height)
          sprite.ox, sprite.oy = width / 2, height
          sprite.x, sprite.y = 144 + direction * 160, 330
          sprite.zoom_x = sprite.zoom_y = 2
          canvas.draw_text(sprite.x - 45, 355, 120, 32, %w[Down Left Right Up][direction])
          sprites << sprite
          characters << [sprite, direction, width, height]
        end
      else
        sprite = Tidebound::Presentation::OwnedSprite.new(viewport)
        sprite.bitmap = Bitmap.new(path)
        sprite.ox, sprite.oy = spec["anchor"] || [sprite.bitmap.width / 2, sprite.bitmap.height / 2]
        sprite.zoom_x = sprite.zoom_y = spec.fetch("scale", 1)
        sprite.x, sprite.y = 384, 270
        canvas.fill_rect(364, 270, 40, 1, Color.new(240, 180, 80))
        canvas.fill_rect(384, 250, 1, 40, Color.new(240, 180, 80))
        sprites << sprite
      end
    end
    sound&.call
    Graphics.transition(0)
    count = 0
    loop do
      characters.each do |sprite, direction, width, height|
        sprite.src_rect.set(((count / 8) % 4) * width, direction * height, width, height)
      end
      sprites.each(&:update)
      Graphics.update
      Input.update
      count += 1
      sound&.call if Input.trigger?(Input::USE)
      break if Input.trigger?(Input::BACK) || (frames && count >= frames)
    end
    if capture
      image = Graphics.snap_to_bitmap
      image.to_file(capture)
      image.dispose
    end
  ensure
    sprites&.each(&:dispose)
    sheet&.dispose
    background&.bitmap&.dispose
    background&.dispose
    viewport&.dispose
    pbBGMStop
    pbBGSStop
    pbMEStop
    pbSEStop
  end
end
