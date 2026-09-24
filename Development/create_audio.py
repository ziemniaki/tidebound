from pathlib import Path
import numpy as np
import wave,subprocess
ROOT=Path(__file__).resolve().parent.parent
out=ROOT/'Audio'/'BGM'
sr=22050;seconds=32;n=sr*seconds;t=np.arange(n)/sr
rng=np.random.default_rng(260908)
for name,notes,noiselevel in [('Tidebound Shore',[146.832,220.0,261.626,329.628],.07),('Tidebound Stillness',[110,164.814,220,246.942],.025)]:
    raw=rng.normal(size=n)
    freq=np.fft.rfftfreq(n,1/sr)
    spectrum=np.fft.rfft(raw)/(1+freq/140)**1.4
    noise=np.fft.irfft(spectrum,n);noise/=max(np.std(noise),.001)
    sound=noise*noiselevel*(.6+.4*np.sin(2*np.pi*t/16)**2)
    for i,f in enumerate(notes):
        # Integer loop periods keep the long pad seamless at the loop point.
        f=round(f*seconds)/seconds
        sound+=.055*np.sin(2*np.pi*f*t)*(.6+.4*np.cos(2*np.pi*t/seconds+i))
        sound+=.014*np.sin(2*np.pi*f*2*t)
    for start,f in [(3,notes[2]*2),(14,notes[1]*2),(23,notes[3]*2)]:
        u=np.maximum(t-start,0);env=(t>=start)*(1-np.exp(-u*25))*np.exp(-u*.9)
        sound+=.1*env*np.sin(2*np.pi*f*t)
    # Raise the existing mix linearly, keeping the music and dynamics intact.
    master_gain=2.0 if name=='Tidebound Shore' else 2.5
    sound=np.tanh(sound)*.65*master_gain
    assert np.max(np.abs(sound))<.75, 'Unexpected master peak'
    stereo=np.stack([sound,np.roll(sound,180)],axis=1)
    rawpath=out/(name+'.wav')
    with wave.open(str(rawpath),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((stereo*32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(rawpath),'-c:a','libvorbis','-q:a','4',str(out/(name+'.ogg'))],check=True)
    rawpath.unlink()
    print(name, '32-second stereo loop', 'peak',round(float(np.max(np.abs(sound))),3))
