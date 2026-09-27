# Give the original Tidebound loops one consistent in-game level. Battle and
# victory metadata pass 100 by default.
# Apply this before Essentials applies the player's music volume preference.
module Tidebound
  module AudioMix
    TRACKS = %w[shore stillness].freeze
    LEVEL = 80
    module_function
    def volume(name, requested)
      basename = name.to_s.tr("\\", "/").split("/").last.to_s.sub(/\.(ogg|wav|mp3|mid)$/i, "")
      return requested unless TRACKS.include?(basename)
      [requested, LEVEL].min
    end
  end
end

module TideboundMusicPlayback
  def bgm_play_internal2(name, volume, pitch, position, track = nil)
    super(name, Tidebound::AudioMix.volume(name, volume), pitch, position, track)
  end
end
Game_System.prepend(TideboundMusicPlayback)
