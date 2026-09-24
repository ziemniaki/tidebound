#!/bin/sh
# Mechanical extraction of the retained generated atlas; ImageMagick required.
set -eu
art_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
game_dir=$(CDPATH= cd -- "$art_dir/../../.." && pwd)
work_dir="$art_dir/exported"
mkdir -p "$work_dir"
convert "$art_dir/source.png" -crop 804x672+83+128 +repage -channel A -threshold 50% +channel -filter point -resize 56x48 -dither None -colors 12 "$work_dir/front.png"
convert "$art_dir/source.png" -crop 692x672+999+128 +repage -channel A -threshold 50% +channel -filter point -resize 56x54 -dither None -colors 12 "$work_dir/back.png"
python3 "$art_dir/mouth_detail.py"
convert "$work_dir/front.png" -filter point -resize 200% -gravity center -background none -extent 160x160 "$game_dir/Graphics/Pokemon/Front/GLACIVERM.png"
convert "$work_dir/back.png" -filter point -resize 200% -gravity south -background none -extent 160x160 "$game_dir/Graphics/Pokemon/Back/GLACIVERM.png"
convert "$work_dir/front.png" -filter point -resize 24x22 -resize 200% -gravity center -background none -extent 64x64 "$work_dir/icon1.png"
python3 "$art_dir/icon_detail.py"
convert "$work_dir/icon1.png" -roll +0-2 "$work_dir/icon2.png"
convert "$work_dir/icon1.png" "$work_dir/icon2.png" +append "$game_dir/Graphics/Pokemon/Icons/GLACIVERM.png"
cp "$game_dir/Graphics/Pokemon/Front/GLACIVERM.png" "$game_dir/Graphics/Pokemon/Front shiny/GLACIVERM.png"
cp "$game_dir/Graphics/Pokemon/Back/GLACIVERM.png" "$game_dir/Graphics/Pokemon/Back shiny/GLACIVERM.png"
