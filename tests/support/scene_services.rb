# Headless scenarios supply the minigame result; rule/update tests remain real.
class Scene_TideboundMending
  def main
    $hideout_plays = ($hideout_plays || 0) + 1
    $hideout_result != false
  end
end

Tone = Struct.new(:red, :green, :blue, :gray)
class HeadlessScreen
  attr_reader :tone
  def start_tone_change(tone, _duration)
    @tone = tone
  end
end
$game_screen = HeadlessScreen.new
class Game_Map
  attr_accessor :fog_name, :fog_opacity, :fog_zoom, :fog_sx, :fog_sy, :fog_blend_type
end
