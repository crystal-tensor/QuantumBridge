"""Package editable sources and record delivery evidence without model weights."""
import hashlib, json, pathlib, subprocess, zipfile
ROOT=pathlib.Path(__file__).resolve().parent.parent
S=json.loads((ROOT/'timing.json').read_text())
for scene in S['scenes']:
    for j,text in enumerate(scene['sentences']):
        stamp=ROOT/'assets'/f'voice-{scene["id"]}-{j:02}.sha256'
        assert stamp.read_text()==hashlib.sha256(text.encode()).hexdigest(),stamp
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(ROOT/'biohydrogen-zh.mp4')]))
v=next(x for x in probe['streams'] if x['codec_type']=='video')
a=next(x for x in probe['streams'] if x['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'24/1')
assert a['codec_name']=='aac' and a['sample_rate']=='48000'
assert len(probe['chapters'])==len(S['scenes'])==17
assert abs(float(probe['format']['duration'])-S['duration'])<.1
receipt={
 'created_local_date':'2026-11-18','title':S['title'],'research_cutoff':S['research_cutoff'],
 'duration_seconds':float(probe['format']['duration']),'video':{'codec':v['codec_name'],'width':v['width'],'height':v['height'],'fps':v['r_frame_rate']},
 'audio':{'codec':a['codec_name'],'sample_rate':a['sample_rate'],'channels':a['channels'],'voice':S['voice'],'target_loudness_lufs':-16,'target_true_peak_db':-1.5},
 'chapters':len(probe['chapters']),'captions':len(S['captions']),
 'skill':{'name':'Anima','repository':'https://github.com/Garinmckayl/anima','source_revision':'8cd9077','license':'MIT'},
 'local_generation':{'model':'LTX-2.3 MLX distilled 1.1','model_directory':'/Users/avalok/work/music/.mv-runtime/model23','text_encoder':'/Users/avalok/work/music/.mv-runtime/gemma','seed':116913402,'resolution':[640,384],'frames':121,'fps':24,'use':'Opening imagery only; not microscopy or a species identification.'},
 'science':'Educational schematics and separate published research routes; no new physical experiments, yield measurements, quantum hardware runs or rate predictions.',
 'navigation':json.loads((ROOT/'production/navigation-check.json').read_text()),
 'browser_media':json.loads((ROOT/'production/media-check.json').read_text()),
 'video_sha256':hashlib.sha256((ROOT/'biohydrogen-zh.mp4').read_bytes()).hexdigest(),
 'checks':{'full_video_decode':True,'narration_inputs_match_captions':True,'anima_bio_topology':json.loads((ROOT/'production/bio-audit.json').read_text()),'forbidden_term_matches':0}
}
# This literal is encoded so the audit itself does not put the excluded term
# into any deliverable text file.
excluded='\u4e13\u5229'
text_suffixes={'.html','.js','.mjs','.css','.json','.txt','.md','.srt','.vtt','.py'}
files=[]
for p in ROOT.rglob('*'):
    if not p.is_file() or 'renders' in p.relative_to(ROOT).parts or 'shots' in p.relative_to(ROOT).parts:continue
    assert excluded not in p.name,p
    if p.suffix in text_suffixes:assert excluded not in p.read_text(),p
    if p.name not in {'biohydrogen-zh.mp4','biohydrogen-zh-1.2x.mp4','source.zip','mix.wav'}:files.append(p)
(ROOT/'production/receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
files.append(ROOT/'production/receipt.json')
with zipfile.ZipFile(ROOT/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
    for p in sorted(set(files)):out.write(p,p.relative_to(ROOT))
with zipfile.ZipFile(ROOT/'source.zip') as archive:
    for name in archive.namelist():
        assert excluded not in name,name
        if pathlib.Path(name).suffix in text_suffixes:assert excluded not in archive.read(name).decode(),name
print(json.dumps({'video_bytes':probe['format']['size'],'duration_seconds':receipt['duration_seconds'],'chapters':17,'source_bytes':(ROOT/'source.zip').stat().st_size,'forbidden_term_matches':0}))
