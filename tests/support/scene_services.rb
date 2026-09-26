# Headless scenarios supply the minigame result; rule/update tests remain real.
class Scene_TideboundMending
  def main
    $hideout_plays = ($hideout_plays || 0) + 1
    $hideout_result != false
  end
end
