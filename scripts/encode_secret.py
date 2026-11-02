#!/usr/bin/env python3
"""Print compressed chapter text for GitHub Actions secret."""
import sys, gzip, base64
from pathlib import Path
data=Path(sys.argv[1]).read_bytes()
print(base64.b64encode(gzip.compress(data,compresslevel=9)).decode("ascii"))
