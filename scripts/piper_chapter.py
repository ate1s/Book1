#!/usr/bin/env python3
"""OHF Piper chapter narration, paragraph clips, exact measured timing."""
import argparse, gzip, base64, json, os, re, subprocess, wave
from pathlib import Path

VOICES = {"narrator":"ru_RU-dmitri-medium","eugene":"ru_RU-ruslan-medium","other":"ru_RU-irina-medium"}
def read_source(path):
    if path:
        return Path(path).read_text(encoding="utf-8")
    encoded=os.environ.get("CHAPTER_TEXT_GZIP_B64","")
    if not encoded:
        raise SystemExit("Set CHAPTER_TEXT_GZIP_B64 GitHub secret or --text file")
    return gzip.decompress(base64.b64decode(encoded)).decode("utf-8")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--text")
    parser.add_argument("--output",default="output/piper_chapter01")
    parser.add_argument("--voice",choices=list(VOICES),default="narrator")
    args=parser.parse_args()
    text=read_source(args.text)
    paragraphs=[re.sub(r"\s+"," ",p).strip() for p in re.split(r"\n\s*\n",text) if p.strip()]
    if not paragraphs: raise SystemExit("Empty chapter")
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    model=VOICES[args.voice]
    clips=[];events=[];cursor=0.0
    for idx,paragraph in enumerate(paragraphs,1):
        # Limit long paragraphs to keep synthesis reliable.
        parts=re.findall(r".{1,320}(?:[.!?…](?=\s|$)|$)",paragraph)
        if not parts: parts=[paragraph]
        for part in parts:
            part=part.strip()
            if not part: continue
            clip=out/f"clip_{len(clips)+1:04d}.wav"
            subprocess.run(["python","-m","piper","-m",model,"-f",str(clip)],input=part,text=True,check=True)
            with wave.open(str(clip),"rb") as wf:
                duration=wf.getnframes()/wf.getframerate()
            events.append({"index":len(events)+1,"start":round(cursor,3),"end":round(cursor+duration,3),"voice":args.voice,"text":part})
            cursor+=duration
            clips.append(clip)
    # WAV concat by ffmpeg filter: re-encode to consistent PCM
    concat=out/"clips.txt"
    concat.write_text("".join("file '"+p.name+"'\n" for p in clips),encoding="utf-8")
    wav=out/"chapter01.wav"
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-ar","22050","-ac","1","-c:a","pcm_s16le",str(wav)],check=True)
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(wav),"-c:a","aac","-b:a","128k",str(out/"chapter01.m4a")],check=True)
    (out/"timing.json").write_text(json.dumps({"voice":model,"duration":round(cursor,3),"segments":events},ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Done: {len(events)} clips; {cursor:.1f} seconds; {wav}")
if __name__=="__main__":
    main()
