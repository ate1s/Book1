#!/usr/bin/env python3
"""Generate original placeholder visuals and synthetic audio for CI smoke test."""
import json,math,struct,wave
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
base=Path("demo");base.mkdir(exist_ok=True)
scenes=[]
for i in range(12):
 image=Image.new("RGB",(1280,720),(14+i*4,20+i*3,36+i*2))
 d=ImageDraw.Draw(image)
 d.rectangle((65,65,1215,655),outline=(190,165,125),width=5)
 d.text((100,120),f"BOOK1 / SCENE {i+1:02}",fill=(240,215,170))
 d.text((100,200),"Demo frames - replace with story illustrations",fill=(220,220,220))
 path=base/f"scene_{i+1:02}.jpg";image.save(path)
 scenes.append({"start":i*2,"end":(i+1)*2,"image":str(path)})
rate=16000
with wave.open(str(base/"test.wav"),"wb") as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
 for j in range(rate*24):
  sample=int(900*math.sin(2*math.pi*220*j/rate))
  w.writeframesraw(struct.pack("<h",sample))
(base/"timeline.json").write_text(json.dumps({"audio":str(base/"test.wav"),"scenes":scenes},indent=2))
print("Created 12 demo frames, audio and timeline")
