# TEST ONLY: verify the actual Essentials -> native Audio path and saved-map mix.
$stdout.sync = true
module AudioMixCallCapture
  def bgm_play(*args)
    ($tb_bgm_calls ||= []) << args
    super(*args)
  end
end
Audio.singleton_class.prepend(AudioMixCallCapture)
class Scene_TideboundTitle
  def main
    SaveData.mark_values_as_unloaded
    Game.load(SaveData.get_data_from_file('chosen-party.rxdata'))
  end
end
module AudioMixNativeCheck
  def update
    super
    return if $tb_audio_checked || !$player || !$game_map || !$game_system
    $tb_audio_checked = true
    run_audio_mix_check
  end

  def run_audio_mix_check
    $PokemonSystem.bgmvolume = 80
    check_bgm('saved map', 'Tidebound Shore', 45, 100, 64)
    check_bgm('exploration', 'Tidebound Stillness', 80, 100, 64)
    battle = pbGetWildBattleBGM([])
    raise "battle track #{battle.name}:#{battle.volume}" unless battle.name == 'Tidebound Stillness' && battle.volume == 100
    check_bgm('battle', battle.name, battle.volume, battle.pitch, 64)
    check_bgm('victory', '../../Audio/BGM/Tidebound Stillness', 100, 100, 64)
    check_bgm('bird prelude', 'Tidebound Stillness', 25, 80, 52)
    $PokemonSystem.bgmvolume = 40
    check_bgm('slider', 'Tidebound Stillness', 100, 100, 32)
    raise 'other music changed' unless Tidebound::AudioMix.volume('Pallet Town', 100, 100) == 100
    File.write('AUDIO_MIX_PASS.txt', 'PASS: actual native Audio playback, saved map, exploration, battle, victory, prelude, slider, unrelated track.\n')
    puts 'AUDIO_MIX_PASS'
    exit
  end

  def check_bgm(label, name, volume, pitch, expected)
    $tb_bgm_calls = []
    pbBGMPlay(name, volume, pitch)
    actual = $tb_bgm_calls.last
    raise "#{label}: #{actual.inspect}, expected #{expected}" unless actual && actual[1] == expected
  end
end
Scene_Map.prepend(AudioMixNativeCheck)
