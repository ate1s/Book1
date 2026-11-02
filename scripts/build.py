#!/usr/bin/env python3
"""Build synchronized video from scene timeline; requires ffmpeg."""
import json, subprocess, argparse
from pathlib import Path

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--timeline",required=True)
 p.add_argument("--output",default="output/chapter.mp4")
 args=p.parse_args()
 data=json.loads(Path(args.timeline).read_text(encoding="utf-8"))
 scenes=data["scenes"]
 if not scenes: raise ValueError("No scenes")
 Path(args.output).parent.mkdir(parents=True,exist_ok=True)
 clips=[]
 for i,s in enumerate(scenes):
  start,end=float(s["start"]),float(s["end"])
  if end<=start: raise ValueError(f"Invalid interval {i}")
  image=Path(s["image"])
  if not image.exists(): raise FileNotFoundError(image)
  clip=Path(args.output).parent/f"segment_{i:04d}.mp4"
  subprocess.run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",str(image),"-t",str(end-start),"-vf","scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p","-r","24","-c:v","libx264","-preset","veryfast","-an",str(clip)],check=True)
  clips.append(clip)
 concat=Path(args.output).parent/"concat.txt"
 concat.write_text("".join("file '"+c.name+"'\n" for c in clips))
 video=Path(args.output).parent/"silent.mp4"
 subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(video)],check=True)
 subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(video),"-i",data["audio"],"-c:v","copy","-c:a","aac","-shortest","-movflags","+faststart",args.output],check=True)
 print(args.output)

if __name__=="__main__": main()
