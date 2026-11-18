"""Generate sentence-level Xiaoxiao narration and exact, measured edit timings."""
import asyncio, json, subprocess, pathlib, hashlib
import edge_tts

ROOT = pathlib.Path(__file__).resolve().parent.parent
STORY = json.loads((ROOT/'production/story.json').read_text())
ASSETS = ROOT/'assets'

def duration(path):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)]))

async def main():
    gate = asyncio.Semaphore(3)
    async def make(scene_id,j,text):
        path = ASSETS/f'voice-{scene_id}-{j:02}.mp3'
        digest = hashlib.sha256(text.encode()).hexdigest()
        stamp = path.with_suffix('.sha256')
        async with gate:
            if not path.exists() or not stamp.exists() or stamp.read_text()!=digest:
                for attempt in range(3):
                    try:
                        await edge_tts.Communicate(text,'zh-CN-XiaoxiaoNeural',rate='-3%').save(str(path))
                        stamp.write_text(digest)
                        break
                    except Exception:
                        if attempt==2: raise
                        await asyncio.sleep(1)
        return duration(path)
    jobs=[make(scene['id'],j,s) for i,scene in enumerate(STORY['scenes']) for j,s in enumerate(scene['sentences'])]
    durations=iter(await asyncio.gather(*jobs))
    clock=0; captions=[]; edits=[]; script=[]
    for i,scene in enumerate(STORY['scenes']):
        start=clock; clock+=1.2
        script.append(scene['title']+'\n'+'\n'.join(scene['sentences']))
        for j,sentence in enumerate(scene['sentences']):
            d=next(durations)
            captions.append({'start':round(clock,3),'end':round(clock+d,3),'text':sentence})
            edits.append({'start':round(clock,3),'duration':d,'file':f'voice-{scene["id"]}-{j:02}.mp3'})
            clock+=d+0.45
        clock+=1.3
        scene.update(start=round(start,3),end=round(clock,3),duration=round(clock-start,3))
    STORY.update(duration=round(clock,3),captions=captions,audio=edits,voice='zh-CN-XiaoxiaoNeural')
    (ROOT/'timing.json').write_text(json.dumps(STORY,ensure_ascii=False,indent=2))
    (ROOT/'SCRIPT.txt').write_text('\n\n'.join(script))
    def ts(t,sep=','):
        ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}{sep}{ms%1000:03}'
    (ROOT/'captions.srt').write_text('\n\n'.join(f'{i+1}\n{ts(c["start"])} --> {ts(c["end"])}\n{c["text"]}' for i,c in enumerate(captions))+'\n')
    (ROOT/'captions.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(f'{ts(c["start"],".")} --> {ts(c["end"],".")}\n{c["text"]}' for c in captions)+'\n')
    print(json.dumps({'duration':clock,'scenes':len(STORY['scenes']),'sentences':len(captions)}))

asyncio.run(main())
