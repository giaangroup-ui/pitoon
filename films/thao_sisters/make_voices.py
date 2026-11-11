#!/usr/bin/env python3
"""Generate all Vietnamese edge-tts lines with character formants. Free only. Retries flaky TTS."""
import json, sys, time, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0, str(Path("/workspace/pitoon/tools")))
from pitoon_pipeline import voice, save, SR

MAP={
  "narrator": {"voice":"man"},
  "child_girl_older": {"voice":"child_girl"},
  "child_girl_younger": {"voice":"child_girl"},
  "child_boy": {"voice":"child_boy"},
  "woman": {"voice":"woman"},
}

def main():
    cfg=json.load(open(ROOT/"scene.json"))
    out=ROOT/"audio"/"voices"; out.mkdir(parents=True, exist_ok=True)
    for i,l in enumerate(cfg["lines"]):
        wav=out/f"l{i:02d}_{l['scene']}_{l['who'].replace(' ','_')}.wav"
        if wav.exists() and wav.stat().st_size>1000:
            print("skip", wav.name); continue
        ln=dict(l); meta=MAP.get(ln.get("voice"), {})
        ln["voice"]=meta.get("voice", ln.get("voice","man"))
        tmp=str(out/f"raw_{i:02d}")
        last=None
        for attempt in range(1,6):
            try:
                x=voice(ln, tmp)
                save(str(wav), x)
                print(f"ok {wav.name} {len(x)/SR:.2f}s")
                last=None
                break
            except Exception as e:
                last=e; print(f"retry {attempt} {wav.name}: {e}"); time.sleep(1.5+attempt)
        if last: raise last
    print("done", len(cfg["lines"]), "lines")

if __name__=="__main__":
    main()
