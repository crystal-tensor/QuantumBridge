"""Mux the rendered picture, mix and chapters into the final delivery."""
import json, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parent.parent
story=json.loads((ROOT/'timing.json').read_text())
metadata=[';FFMETADATA1','title='+story['title']]
for scene in story['scenes']:
    metadata+=['[CHAPTER]','TIMEBASE=1/1000',f'START={round(scene["start"]*1000)}',f'END={round(scene["end"]*1000)}','title='+scene['title']]
(ROOT/'production/chapters.txt').write_text('\n'.join(metadata)+'\n')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(ROOT/'production/renders/picture.mp4'),'-i',str(ROOT/'assets/mix.wav'),'-i',str(ROOT/'production/chapters.txt'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-af','loudnorm=I=-16:TP=-1.5:LRA=7','-movflags','+faststart','-shortest',str(ROOT/'biohydrogen-zh.mp4')],check=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss','5','-i',str(ROOT/'biohydrogen-zh.mp4'),'-frames:v','1','-q:v','2',str(ROOT/'assets/poster.jpg')],check=True)
print('Final MP4 and poster ready')
