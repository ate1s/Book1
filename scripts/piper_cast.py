#!/usr/bin/env python3
"""Multi-character OHF Piper synthesis; one model load per voice."""
import argparse,base64,gzip,json,os,re,subprocess,wave
from pathlib import Path
from piper import PiperVoice
P={
"narrator":("ru_RU-dmitri-medium",1,0.97),
"alexander":("ru_RU-dmitri-medium",1.08,1.03),
"eugene":("ru_RU-ruslan-medium",1.12,1.09),
"inigo":("ru_RU-ruslan-medium",0.92,0.93),
"captor_leader":("ru_RU-dmitri-medium",0.86,0.91),
"captor_second":("ru_RU-ruslan-medium",0.83,0.98),
"epigraph":("ru_RU-irina-medium",0.95,0.94),
"prisoner":("ru_RU-irina-medium",1.07,1.05)}
D={
"Александр. Светлые волосы":"captor_leader",
"Эжен. Рыжий. Проблемы":"captor_leader",
"Рыжий лучше":"captor_second",
"Отлично, продолжим":"captor_leader",
"Добро пожаловать!":"captor_leader",
"Только я его понял?":"eugene",
"Я Эжен. Нехило":"eugene",
"Александр,":"alexander",
"Иниго,":"inigo"}
def main():
 p=argparse.ArgumentParser();p.add_argument("--text");p.add_argument("--output",default="output/piper_chapter01");p.add_argument("--assignments",default="scenes/chapter01_speaker_overrides.json");a=p.parse_args()
 if a.text:content=Path(a.text).read_text(encoding="utf8")
 else:
  secret=os.environ.get("CHAPTER_TEXT_GZIP_B64","")
  if not secret:raise SystemExit("Missing CHAPTER_TEXT_GZIP_B64 secret")
  content=gzip.decompress(base64.b64decode(secret)).decode("utf8")
 overrides=json.loads(Path(a.assignments).read_text(encoding="utf8")) if Path(a.assignments).exists() else {}
 rows=[]
 for idx,line in enumerate(content.splitlines(),1):
  line=line.strip()
  if not line:continue
  role="epigraph" if idx in (2,3) else "narrator"
  if line.startswith(("–","—","-")):
   stripped=line.lstrip("–—- \u00a0")
   for prefix,person in D.items():
    if stripped.startswith(prefix):role=person;break
  role=overrides.get(str(idx),role)
  if role not in P:raise ValueError("Unknown speaker: "+role)
  rows.append({"line":idx,"speaker":role,"text":line})
 out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
 models={name:PiperVoice.load(str(Path("voices")/(name+".onnx"))) for name in {P[r["speaker"]][0] for r in rows}}
 events=[];clips=[];cursor=0.
 for row in rows:
  model,pitch,tempo=P[row["speaker"]]
  for sentence in re.split(r"(?<=[.!?…])\s+",row["text"]):
   sentence=sentence.strip()
   if not sentence:continue
   n=len(clips)+1;raw=out/f"raw_{n:04}.wav";clip=out/f"clip_{n:04}.wav"
   with wave.open(str(raw),"wb") as wf:models[model].synthesize_wav(sentence,wf)
   with wave.open(str(raw),"rb") as wf:rate=wf.getframerate()
   filt=f"asetrate={int(rate*pitch)},aresample={rate},atempo={tempo/pitch:.6f}"
   subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(raw),"-af",filt,"-c:a","pcm_s16le",str(clip)],check=True)
   raw.unlink()
   with wave.open(str(clip),"rb") as wf:duration=wf.getnframes()/wf.getframerate()
   events.append({"index":n,"line":row["line"],"start":round(cursor,3),"end":round(cursor+duration,3),"speaker":row["speaker"],"text":sentence})
   cursor+=duration;clips.append(clip)
 concat=out/"clips.txt"
 concat.write_text("".join("file '"+c.name+"'\n" for c in clips),encoding="utf8")
 wav=out/"chapter01.wav"
 subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-c:a","pcm_s16le",str(wav)],check=True)
 subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(wav),"-c:a","aac","-b:a","128k",str(out/"chapter01.m4a")],check=True)
 (out/"timing.json").write_text(json.dumps({"duration":round(cursor,3),"segments":events},ensure_ascii=False,indent=2),encoding="utf8")
 (out/"speaker_review.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf8")
 print(f"Cast: {len(events)} segments, {cursor:.1f}s")
if __name__=="__main__":main()
