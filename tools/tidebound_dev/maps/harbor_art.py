def wooden_village(atlas):
    result = atlas.copy()
    for sx, sy in [(0, 227), (4, 228)]:
        house = atlas.crop((sx * 32, sy * 32, (sx + 4) * 32, (sy + 4) * 32))
        px = house.load()
        for y in range(128):
            for x in range(128):
                r, g, b, a = px[x, y]
                if not a:
                    continue
                # Original glass includes blue doors, retained for geometric fidelity.
                if b >= 180 and g > r + 25 and b > g + 25:
                    continue
                lum = (r + g + b) // 3
                if y < 96:
                    # Old shingles; original raised seams and ragged edges survive.
                    px[x, y] = (int(lum * 0.60) + 24, int(lum * 0.57) + 24, int(lum * 0.55) + 28, a)
                else:
                    # Walls acquire salt-worn horizontal timber courses.
                    if lum < 90:
                        px[x, y] = (61, 53, 51, a)
                    elif y >= 123:
                        v = (x // 12 + (y // 4)) % 3
                        px[x, y] = (112 + v * 10, 116 + v * 9, 118 + v * 8, a)
                    else:
                        grain = 7 if y % 6 == 0 else -13 if y % 6 == 5 else 0
                        px[x, y] = (
                            max(0, int(lum * 0.52) + 46 + grain),
                            max(0, int(lum * 0.42) + 35 + grain),
                            max(0, int(lum * 0.32) + 30 + grain),
                            a,
                        )
        # Low-contrast pegs and irregular wood grain on opaque wall portions only.
        for y in [100, 106, 112, 118]:
            for x in [6, 38, 64, 112]:
                r, g, b, a = px[x, y]
                if a and not (b >= 180 and g > r + 25 and b > g + 25):
                    px[x, y] = (78, 66, 55, a)
        result.paste(house, (sx * 32, sy * 32))
    return result
