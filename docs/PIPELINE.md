# Production pipeline

1. Extract chapter locally from a legally obtained EPUB. Do not commit source book text to a public repository without permission.
2. Split chapter into chronological beats with verbatim anchors and identify speakers.
3. Produce separate speech clips and a final mixed WAV; keep speaker IDs stable.
4. Align the final audio to transcript using WhisperX; review difficult names manually.
5. Assign an illustration to each event; store exact start/end in JSON.
6. Render with scripts/build.py. GitHub Actions is for montage, not GPU image generation.

## Smoke test
Run `python -m pip install -r requirements.txt`, `python scripts/make_demo.py`, then `python scripts/build.py --timeline demo/timeline.json --output output/demo.mp4`.

Demo visuals and test audio are synthetic placeholders. No real chapter audio or illustrations are bundled.
