#!/usr/bin/env bash
set -euo pipefail
art_dir="$(cd "$(dirname "$0")" && pwd)"
game_dir="$(cd "$art_dir/../../.." && pwd)"
# The generator supplied a chroma-key atlas. Mechanical key removal/extraction only.
convert "$art_dir/source.png" -alpha on -fuzz 15% -transparent '#ff00ff' "$art_dir/keyed.png"
convert "$art_dir/keyed.png" -crop 627x780+0+0 +repage -trim +repage -filter point -resize 53x61 -colors 16 -filter point -resize 200% -gravity center -background none -extent 160x160 "$game_dir/Graphics/Pokemon/Front/MOONKERN.png"
convert "$art_dir/keyed.png" -crop 627x780+627+0 +repage -trim +repage -filter point -resize 59x68 -colors 16 -filter point -resize 200% -gravity south -background none -extent 160x160 "$game_dir/Graphics/Pokemon/Back/MOONKERN.png"
convert "$art_dir/keyed.png" -crop 627x474+0+780 +repage -trim +repage -filter point -resize 23x27 -colors 16 -filter point -resize 200% -gravity center -background none -extent 64x64 "$art_dir/icon-0.png"
# A two-pixel bob of the same face preserves the correct forward-facing icon.
convert "$art_dir/icon-0.png" -background none -gravity north -splice 0x2 -gravity north -crop 64x64+0+0 +repage "$art_dir/icon-1.png"
convert "$art_dir/icon-0.png" "$art_dir/icon-1.png" +append "$game_dir/Graphics/Pokemon/Icons/MOONKERN.png"
cp "$game_dir/Graphics/Pokemon/Front/MOONKERN.png" "$game_dir/Graphics/Pokemon/Front shiny/MOONKERN.png"
cp "$game_dir/Graphics/Pokemon/Back/MOONKERN.png" "$game_dir/Graphics/Pokemon/Back shiny/MOONKERN.png"
