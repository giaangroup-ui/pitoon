#!/usr/bin/env python3
"""Detect music beats (onset strength peaks) and snap cut times to nearest beat.
Usage: beats.py audio.wav [--cuts 5,10,15]  → JSON list of snapped times."""
import argparse, json, subprocess as sp, tempfile, os
import numpy as np

def load_wav(path, sr=22050):
    with tempfile.NamedTemporaryFile(suffix=".f32") as t:
        sp.run(["ffmpeg","-loglevel","error","-y","-i",path,"-ac","1","-ar",str(sr),"-f","f32le",t.name], check=True)
        return np.fromfile(t.name, dtype=np.float32), sr

def onset_beats(y, sr, hop=512):
    # spectral flux onset
    n_fft=1024; win=np.hanning(n_fft).astype(np.float32)
    mags=[]
    for i in range(0, len(y)-n_fft, hop):
        mag=np.abs(np.fft.rfft(y[i:i+n_fft]*win)); mags.append(mag)
    mags=np.array(mags)
    flux=np.maximum(0, np.diff(mags, axis=0).sum(axis=1)); flux=np.concatenate([[0],flux])
    # normalize + peak pick
    flux=(flux-flux.mean())/(flux.std()+1e-9)
    peaks=[]
    for i in range(2,len(flux)-2):
        if flux[i]>1.0 and flux[i]>flux[i-1] and flux[i]>flux[i+1]:
            if not peaks or (i-peaks[-1])>int(0.25*sr/hop): peaks.append(i)
    times=np.array(peaks)*hop/sr
    return times, flux

def snap(cuts, beats, max_shift=0.35):
    out=[]
    for c in cuts:
        if len(beats)==0: out.append(c); continue
        j=int(np.argmin(np.abs(beats-c))); b=float(beats[j])
        out.append(b if abs(b-c)<=max_shift else c)
    return out

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("audio"); ap.add_argument("--cuts",default="")
    a=ap.parse_args(); y,sr=load_wav(a.audio); beats,_=onset_beats(y,sr)
    cuts=[float(x) for x in a.cuts.split(",") if x.strip()]
    print(json.dumps({"beats":[round(float(b),3) for b in beats[:80]],
                      "snapped":snap(cuts,beats) if cuts else []}, ensure_ascii=False))
