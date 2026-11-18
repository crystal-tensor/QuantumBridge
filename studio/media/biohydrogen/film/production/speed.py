"""Create the 1.2x delivery with pitch-preserving audio and retimed captions."""
import json, pathlib, subprocess

ROOT=pathlib.Path(__file__).resolve().parent.parent
RATE=1.2
story=json.loads((ROOT/'timing.json').read_text())
metadata=[';FFMETADATA1','title='+story['title']+' · 1.2x']
for scene in story['scenes']:
    metadata+=['[CHAPTER]','TIMEBASE=1/1000',f'START={round(scene["start"]/RATE*1000)}',f'END={round(scene["end"]/RATE*1000)}','title='+scene['title']]
chapters=ROOT/'production/chapters-1.2x.txt'
chapters.write_text('\n'.join(metadata)+'\n')

def timestamp(t,sep=','):
    ms=round(t/RATE*1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}{sep}{ms%1000:03}'

captions=story['captions']
(ROOT/'captions-1.2x.srt').write_text('\n\n'.join(f'{i+1}\n{timestamp(c["start"])} --> {timestamp(c["end"])}\n{c["text"]}' for i,c in enumerate(captions))+'\n')
(ROOT/'captions-1.2x.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(f'{timestamp(c["start"],".")} --> {timestamp(c["end"],".")}\n{c["text"]}' for c in captions)+'\n')

output=ROOT/'biohydrogen-zh-1.2x.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',
    '-i',str(ROOT/'biohydrogen-zh.mp4'),'-i',str(chapters),
    '-map','0:v:0','-map','0:a:0','-map_metadata','1','-map_chapters','1',
    '-vf','setpts=(PTS-STARTPTS)/1.2,fps=24','-af','atempo=1.2',
    '-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',
    '-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',
    str(output)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(output)]))
duration=float(probe['format']['duration'])
assert abs(duration-story['duration']/RATE)<.15
video=next(s for s in probe['streams'] if s['codec_type']=='video')
assert [video['width'],video['height'],video['r_frame_rate']]==[1920,1080,'24/1']
assert len(probe['chapters'])==len(story['scenes'])
receipt={'playback_speed':RATE,'duration_seconds':duration,'original_duration_seconds':story['duration'],
    'video':{'width':1920,'height':1080,'fps':24,'codec':'h264'},
    'audio':'AAC, 48000 Hz, atempo=1.2 (preserves pitch)',
    'captions_retimed':len(captions),'chapters_retimed':len(probe['chapters']),
    'bytes':output.stat().st_size}
(ROOT/'production/speed-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
print(json.dumps(receipt))
