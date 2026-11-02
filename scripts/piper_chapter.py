#!/usr/bin/env python3
"""Render Russian speech with OHF Piper. Source stays in Actions secret."""
import argparse, base64, gzip, json, os, re, subprocess, wave
from pathlib import Path
VOICES={"narrator":"ru_RU-dmitri-medium","eugene":"ru_RU-ruslan-medium","other":"ru_RU-irina-medium"}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--text")
    p.add_argument("--voice",choices=VOICES,default="narrator")
    p.add_argument("--output",default="output/piper_chapter01")
    args=p.parse_args()
    if args.text:
        content=Path(args.text).read_text(encoding="utf-8")
    else:
        secret=os.environ.get("CHAPTER_TEXT_GZIP_B64","")
        if not secret: raise SystemExit("Missing CHAPTER_TEXT_GZIP_B64 secret")
        content=gzip.decompress(base64.b64decode(secret)).decode("utf-8")
    paragraphs=[re.sub(r"\s+"," ",v).strip() for v in re.split(r"\n\s*\n",content) if v.strip()]
    if not paragraphs: raise SystemExit("No paragraphs found")
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    model=Path("voices")/(VOICES[args.voice]+".onnx")
    if not model.is_file(): raise SystemExit(f"Missing voice model: {model}")
    segments=[];clips=[];cursor=0.0
    for para in paragraphs:
        # Split at sentence boundaries, retain every word.
        sentences=re.split(r"(?<=[.!?…])\s+",para)
        for sentence in sentences:
            if not sentence.strip(): continue
            clip=out/f"clip_{len(clips)+1:04}.wav"
            subprocess.run(["python","-m","piper","--model",str(model),"--output_file",str(clip)],
                           input=sentence.strip()+"\n",text=True,check=True)
            with wave.open(str(clip),"rb") as f:
                duration=f.getnframes()/f.getframerate()
            segments.append({"index":len(segments)+1,"start":round(cursor,3),"end":round(cursor+duration,3),"voice":args.voice,"text":sentence.strip()})
            cursor+=duration
            clips.append(clip)
    concat=out/"clips.txt"
    concat.write_text("".join("file '"+clip.name+"'\n" for clip in clips),encoding="utf-8")
    wav=out/"chapter01.wav"
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-ac","1","-c:a","pcm_s16le",str(wav)],check=True)
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(wav),"-c:a","aac","-b:a","128k",str(out/"chapter01.m4a")],check=True)
    (out/"timing.json").write_text(json.dumps({"model":model.name,"duration":round(cursor,3),"segments":segments},ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Generated {len(clips)} clips, {cursor:.2f} seconds")
if __name__=="__main__": main()
