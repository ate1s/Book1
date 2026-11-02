# OHF Piper voiceover

Runs in GitHub Actions with no HeyGen, ElevenLabs, or paid API.

## Try the workflow on iPhone
Open Actions → **OHF Piper — Russian Chapter Voiceover** → Run workflow → demo=true. After success download artifact `piper-ru-voiceover` containing WAV, M4A, and segment timing.

## Full chapter without exposing book text publicly
Compress the UTF-8 chapter text with gzip, encode with base64, and create a GitHub Actions repository secret named `CHAPTER_TEXT_GZIP_B64`. The local preparation script is `scripts/encode_secret.py`. Run workflow with demo=false. Do not paste the chapter into an issue, workflow input, or public commit.

## Voices
- narrator: `ru_RU-dmitri-medium`
- eugene: `ru_RU-ruslan-medium`
- other: `ru_RU-irina-medium`

The current full-chapter mode uses **one selected voice per run**. Separate voices per character require a speaker-tagged dialogue script and mixing pass; this is not yet implemented. Timings are measured per synthesized clip, but word-level synchronization is not provided.

Models download at workflow runtime; check model-card licenses before redistribution. This project does not bundle copyrighted text or model weights.
