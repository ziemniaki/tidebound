"""Regenerate ambient loops with NumPy and ffmpeg; preserve old audio on failure."""

from tidebound_dev.paths import ROOT
from pathlib import Path
import subprocess
import tempfile
import wave


def encode_loop(pcm, output, sample_rate):
    output = Path(output)
    # Same filesystem for atomic publication; failed encoding never touches the
    # playable file, and temporary WAV/OGG data is removed on every exit path.
    with tempfile.TemporaryDirectory(prefix=".audio-", dir=output.parent) as temp:
        raw = Path(temp) / "loop.wav"
        encoded = Path(temp) / "loop.ogg"
        with wave.open(str(raw), "wb") as stream:
            stream.setnchannels(2)
            stream.setsampwidth(2)
            stream.setframerate(sample_rate)
            stream.writeframes(pcm)
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-i",
                str(raw),
                "-c:a",
                "libvorbis",
                "-q:a",
                "4",
                str(encoded),
            ],
            check=True,
        )
        encoded.replace(output)


def main():
    import numpy as np

    out = ROOT / "game/Audio/BGM"
    sr = 22050
    seconds = 32
    n = sr * seconds
    t = np.arange(n) / sr
    rng = np.random.default_rng(260908)
    for name, notes, noiselevel in [
        ("Tidebound Shore", [146.832, 220.0, 261.626, 329.628], 0.07),
        ("Tidebound Stillness", [110, 164.814, 220, 246.942], 0.025),
    ]:
        raw = rng.normal(size=n)
        freq = np.fft.rfftfreq(n, 1 / sr)
        spectrum = np.fft.rfft(raw) / (1 + freq / 140) ** 1.4
        noise = np.fft.irfft(spectrum, n)
        noise /= max(np.std(noise), 0.001)
        sound = noise * noiselevel * (0.6 + 0.4 * np.sin(2 * np.pi * t / 16) ** 2)
        for i, f in enumerate(notes):
            # Integer loop periods keep the long pad seamless at the loop point.
            f = round(f * seconds) / seconds
            sound += (
                0.055
                * np.sin(2 * np.pi * f * t)
                * (0.6 + 0.4 * np.cos(2 * np.pi * t / seconds + i))
            )
            sound += 0.014 * np.sin(2 * np.pi * f * 2 * t)
        for start, f in [(3, notes[2] * 2), (14, notes[1] * 2), (23, notes[3] * 2)]:
            u = np.maximum(t - start, 0)
            env = (t >= start) * (1 - np.exp(-u * 25)) * np.exp(-u * 0.9)
            sound += 0.1 * env * np.sin(2 * np.pi * f * t)
        # Raise the existing mix linearly, keeping the music and dynamics intact.
        master_gain = 2.0 if name == "Tidebound Shore" else 2.5
        sound = np.tanh(sound) * 0.65 * master_gain
        assert np.max(np.abs(sound)) < 0.75, "Unexpected master peak"
        stereo = np.stack([sound, np.roll(sound, 180)], axis=1)
        encode_loop((stereo * 32767).astype("<i2").tobytes(), out / (name + ".ogg"), sr)
        print(name, "32-second stereo loop", "peak", round(float(np.max(np.abs(sound))), 3))


if __name__ == "__main__":
    main()
