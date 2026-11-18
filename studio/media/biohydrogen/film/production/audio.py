"""Mix measured narration with an original, quiet synthesized ambient score."""
import json, pathlib, subprocess, wave
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parent.parent
story=json.loads((ROOT/'timing.json').read_text());sr=48000;n=round(story['duration']*sr)
voice=np.zeros(n,dtype=np.float32)
for edit in story['audio']:
    data=subprocess.check_output(['ffmpeg','-hide_banner','-loglevel','error','-i',str(ROOT/'assets'/edit['file']),'-f','f32le','-ac','1','-ar',str(sr),'pipe:1'])
    samples=np.frombuffer(data,dtype='<f4');start=round(edit['start']*sr);end=min(n,start+len(samples))
    voice[start:end]+=samples[:end-start]
# Slow sustained fifths and soft upper harmonics; no generated vocals or borrowed music.
music=np.zeros(n,dtype=np.float32)
chords=[(146.832,220,293.665),(130.813,195.998,261.626),(174.614,261.626,349.228),(164.814,246.942,329.628)]
for start in range(0,n,12*sr):
    length=min(n-start,16*sr);t=np.arange(length,dtype=np.float32)/sr
    env=np.minimum(1,t/3)*np.minimum(1,(length/sr-t)/5)
    pad=np.zeros(length,dtype=np.float32)
    for f in chords[(start//(12*sr))%len(chords)]:
        pad+=np.sin(2*np.pi*f*t)*.55+np.sin(2*np.pi*f*2*t)*.12
    music[start:start+length]+=pad*env*.0055
fade=np.minimum(1,np.arange(n)/sr/3)*np.minimum(1,(n-np.arange(n))/sr/5)
mixed=(voice*.95+music)*fade
stereo=np.stack([mixed,mixed+music*.07],axis=1)
peak=float(np.max(np.abs(stereo)));stereo*=min(1,.93/max(peak,1e-9))
with wave.open(str(ROOT/'assets/mix.wav'),'wb') as out:
    out.setnchannels(2);out.setsampwidth(2);out.setframerate(sr);out.writeframes((stereo*32767).astype('<i2').tobytes())
(ROOT/'production/audio-receipt.json').write_text(json.dumps({'sample_rate':sr,'channels':2,'voice':story['voice'],'pre_limit_peak':peak,'music':'Original procedural ambient score; no external recordings.'},indent=2))
print('Audio ready',story['duration'])
