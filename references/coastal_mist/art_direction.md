# Cloud fog and retained streak effect

Current direction: slow, partially transparent white-grey cloud banks with soft
airbrush edges. No directional rays or straight bands. Use the generated RGBA
pixels unchanged and control opacity and world scale in the renderer.

Built-in image generation was used (no CLI/API fallback). The selected second
result is `content/fogs/coastal_mist.png`; its alpha is retained. Edge alpha is
0–1/255, so repeating the texture does not introduce visible straight seams.

## Generation prompt

Use case: stylized-concept. Asset type: a seamless repeating RGBA ground-fog texture for a top-down night-time island game, square 1024 by 1024. Generate ONLY fog on a genuinely transparent background. The fog consists of irregular soft overlapping white-grey cloud blobs, like very large airbrush dabs, hazy rounded billowing banks with extremely soft feathered translucent edges and partly transparent interiors. Many asymmetrically sized cloud clusters distributed across the tile, with broad clear transparent gaps between them. Larger rounded cloud masses mixed with small diffuse puffs; not a single centred cloud. Gentle cloudy turbulent structure, no sharp detail. Ambient diffuse white to pale neutral grey, no directional highlights or shading. Approximately half the area is clear or very thin. Seamless horizontal and vertical repeat, no visible border or frame. Avoid all straight streaks, parallel bands, diagonal lines, rays, beams, god rays, sunshine, sky, ground, objects, lettering, horizon, hard outlines, opaque backdrop and checkerboard pixels. This is a reusable fog opacity layer; the game will control opacity and slow movement.

## Refinement prompt

Edit this fog texture for use as a looping transparent game overlay. Keep the soft white-grey cloudy masses and diffuse airbrush style, but fix two things: (1) leave a completely transparent margin at least 80 pixels wide on ALL FOUR SIDES; every cloud patch must be fully contained inside that border and taper to zero alpha before reaching it; (2) cloud edges must be extremely soft and diffuse, gradually becoming translucent, with no cutout-looking outlines or grainy speckled edges. Make loosely distributed irregular partly translucent rounded cloud blobs with broad clear gaps between them. Treat it like white-grey airbrush paint sprayed lightly in cloudy patches on transparent glass. The clouds must have smoothly feathered semi-transparent edges and varied internal opacity, not fully opaque white filled shapes. No straight lines, directional streaks, rays or diagonal bands. Do not add background, ground, checkerboard pixels, framing or text.

## Retained effect for a future location

The previous original procedural texture is retained unchanged as
`content/fogs/light_shafts.png`. No current map uses it. Its matching renderer
settings are preserved here for reuse with the existing layered-plane mechanic:

```ruby
LAYERS = [[1.4, 0.75, 12, 1.5, 85, 24], [2.0, 1.15, 6, -0.7, 38, 37]]
tone = Tone.new(-65, -67, -67, 0)
```

The columns are horizontal scale, vertical scale, horizontal wind, vertical
wind, maximum opacity, and density-cycle period. The original implementation
is commit `d359af5`; the shared scrolling, density and lifecycle code remains
in `src/tidebound/presentation/mist.rb`.
