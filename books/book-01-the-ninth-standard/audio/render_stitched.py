#!/usr/bin/env python3
"""Render a chapter through the ElevenLabs API with request stitching.

The whole point of this file is the three lines that pass previous_request_ids,
previous_text and next_text. Without them every chunk is a fresh roll of the
voice -- which is what produced ch7's 469 Hz seam and its 36 over-long pauses
in the final chunk. See the per-chunk table in the session notes.

  python3 render_stitched.py <chunks.json> <voice_id> <outdir> [model]
"""
import json, os, ssl, sys, time, urllib.error, urllib.request

API = "https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128"
KEY = os.environ.get("ELEVEN_API_KEY")
SEED = 20260823          # fixed so a re-render reproduces
CTX = 600                # chars of neighbouring text passed as context
MAX_STITCH = 3           # API ceiling on previous_request_ids

def render(text, vid, model, prev_ids, prev_text, next_text):
    body = {"text": text, "model_id": model, "seed": SEED}
    # These are the fix. previous_request_ids conditions on the actual prior
    # generation, so timbre AND pacing carry across the seam; the text fields
    # tell the model where it is in the sentence rhythm.
    if prev_ids:  body["previous_request_ids"] = prev_ids[-MAX_STITCH:]
    if prev_text: body["previous_text"] = prev_text[-CTX:]
    if next_text: body["next_text"] = next_text[:CTX]

    req = urllib.request.Request(
        API.format(vid=vid), data=json.dumps(body).encode(),
        headers={"xi-api-key": KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, context=ssl.create_default_context()) as r:
        return r.read(), r.headers.get("request-id")

def main():
    chunks = json.load(open(sys.argv[1]))
    vid, outdir = sys.argv[2], sys.argv[3]
    model = sys.argv[4] if len(sys.argv) > 4 else "eleven_multilingual_v2"
    os.makedirs(outdir, exist_ok=True)

    ids, manifest = [], []
    for i, text in enumerate(chunks):
        prev_text = chunks[i-1] if i else None
        next_text = chunks[i+1] if i+1 < len(chunks) else None
        for attempt in range(4):
            try:
                audio, rid = render(text, vid, model, ids, prev_text, next_text)
                break
            except urllib.error.HTTPError as e:
                # 429 is real and recovers when paced; back off rather than hammer.
                wait = 10 * (attempt + 1)
                print(f"  chunk {i+1}: HTTP {e.code}, retry in {wait}s", flush=True)
                if attempt == 3:
                    print(f"  chunk {i+1}: FAILED after 4 attempts"); sys.exit(1)
                time.sleep(wait)
        path = os.path.join(outdir, f"chunk{i+1:02d}.mp3")
        open(path, "wb").write(audio)
        ids.append(rid)
        manifest.append({"chunk": i+1, "chars": len(text), "bytes": len(audio),
                         "request_id": rid, "stitched_on": ids[-MAX_STITCH-1:-1]})
        print(f"  chunk {i+1}/{len(chunks)}  {len(audio):>9,} bytes  rid={rid}"
              f"  stitched_on={len(ids)-1}", flush=True)
        time.sleep(1)      # gentle pacing; 429s appeared at ~40% when pushed

    json.dump(manifest, open(os.path.join(outdir, "chunks.json"), "w"), indent=1)
    print(f"done: {len(chunks)} chunks -> {outdir}")

if __name__ == "__main__":
    if not KEY: sys.exit("ELEVEN_API_KEY not set")
    main()
