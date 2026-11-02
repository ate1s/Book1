#!/usr/bin/env python3
"""Validate illustration/audio timing and missing assets."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("timeline")
p.add_argument("--allow-missing",action="store_true")
args=p.parse_args()
data=json.loads(Path(args.timeline).read_text(encoding="utf-8"))
errors=[]
prev=0.0
for i,s in enumerate(data.get("scenes",[]),1):
 start,end=float(s["start"]),float(s["end"])
 if start<prev-0.02:errors.append(f"scene {i}: overlap")
 if start>prev+0.02:errors.append(f"scene {i}: gap {start-prev:.2f}s")
 if end<=start:errors.append(f"scene {i}: invalid duration")
 if not args.allow_missing and not Path(s["image"]).is_file():errors.append(f"scene {i}: image missing")
 prev=end
if not args.allow_missing and not Path(data["audio"]).is_file():errors.append("audio missing")
print(f"Scenes: {len(data.get('scenes',[]))}; duration: {prev:.2f}s")
if errors:
 print("\n".join(errors));raise SystemExit(1)
print("Timeline validated")
