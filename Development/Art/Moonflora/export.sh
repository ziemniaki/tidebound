#!/usr/bin/env bash
set -euo pipefail
art_dir="$(cd "$(dirname "$0")" && pwd)"
game_dir="$(cd "$art_dir/../../.." && pwd)"
convert "$art_dir/source.png" -alpha on -fuzz 15% -transparent '#ff00ff' "$art_dir/keyed.png"
for view in Front Back; do
 offset=0
 if [ "$view" = Back ]; then offset=803; fi
 convert "$art_dir/keyed.png" -crop "803x980+$offset+0" +repage -trim +repage -filter point -resize 38x46 -colors 8 -filter point -resize 200% -gravity center -background none -extent 160x160 "$game_dir/Graphics/Pokemon/$view/MOONFLORA.png"
 cp "$game_dir/Graphics/Pokemon/$view/MOONFLORA.png" "$game_dir/Graphics/Pokemon/$view shiny/MOONFLORA.png"
done
convert "$art_dir/keyed.png" -crop 803x980+0+0 +repage -trim +repage -filter point -resize 22x27 -colors 8 -filter point -resize 200% -gravity center -background none -extent 64x64 "$art_dir/icon-0.png"
convert "$art_dir/icon-0.png" -background none -gravity north -splice 0x2 -gravity north -crop 64x64+0+0 +repage "$art_dir/icon-1.png"
convert "$art_dir/icon-0.png" "$art_dir/icon-1.png" +append "$game_dir/Graphics/Pokemon/Icons/MOONFLORA.png"
