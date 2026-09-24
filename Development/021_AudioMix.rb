# Give the original Tidebound loops one consistent in-game level. Battle and
# victory metadata pass 100 by default; older saves contain 45-volume maps.
# Apply this before Essentials applies the player's music volume preference.
module Tidebound
  module AudioMix
    TRACKS = ["Tidebound Shore", "Tidebound Stillness"].freeze
    LEVEL = 80
    PRELUDE_LEVEL = 65
    module_function
    def volume(name, requested, pitch)
      basename = name.to_s.tr("\\", "/").split("/").last.to_s.sub(/\.(ogg|wav|mp3|mid)$/i, "")
      return requested unless TRACKS.include?(basename)
      return LEVEL if requested == 45 && pitch == 100
      return PRELUDE_LEVEL if requested == 25 && pitch == 80
      [requested, LEVEL].min
    end
  end
end

module TideboundMusicPlayback
  def bgm_play_internal2(name, volume, pitch, position, track = nil)
    super(name, Tidebound::AudioMix.volume(name, volume, pitch), pitch, position, track)
  end
end
Game_System.prepend(TideboundMusicPlayback)
