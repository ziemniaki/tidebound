#!/usr/bin/env bash
set -euo pipefail
art_dir="$(cd "$(dirname "$0")" && pwd)"
game_dir="$(cd "$art_dir/../../.." && pwd)"
# Mechanical atlas extraction and nearest-neighbor runtime sizing only.
convert "$art_dir/source.png" -crop 627x760+0+0 +repage -channel A -threshold 50% +channel -trim +repage -filter point -resize 42x47 -colors 16 -filter point -resize 200% -gravity center -background none -extent 160x160 "$game_dir/Graphics/Pokemon/Front/SUNKERN_1.png"
convert "$art_dir/source.png" -crop 627x760+627+0 +repage -channel A -threshold 50% +channel -trim +repage -filter point -resize 57x66 -colors 16 -filter point -resize 200% -gravity south -background none -extent 160x160 "$game_dir/Graphics/Pokemon/Back/SUNKERN_1.png"
for frame in 0 1; do
 convert "$art_dir/source.png" -crop "627x494+$((frame * 627))+760" +repage -channel A -threshold 50% +channel -trim +repage -filter point -resize 22x26 -colors 16 -filter point -resize 200% -gravity center -background none -extent 64x64 "$art_dir/icon-$frame.png"
done
convert "$art_dir/icon-0.png" "$art_dir/icon-1.png" +append "$game_dir/Graphics/Pokemon/Icons/SUNKERN_1.png"
# No separate shiny palette is established yet; avoid healthy-form fallback.
cp "$game_dir/Graphics/Pokemon/Front/SUNKERN_1.png" "$game_dir/Graphics/Pokemon/Front shiny/SUNKERN_1.png"
cp "$game_dir/Graphics/Pokemon/Back/SUNKERN_1.png" "$game_dir/Graphics/Pokemon/Back shiny/SUNKERN_1.png"
