#!/usr/bin/env python3
"""Export presets: 16:9 YouTube, 9:16 TikTok/Reels/Zalo (nền mờ), thumbnail 1280x720 + 1080x1920. Usage: export.py film.mp4 out_dir"""
import os, subprocess as sp, sys
P = {"youtube_16x9": "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
     "vertical_9x16": "split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20[bg];[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2"}
def run(film, out):
    os.makedirs(out, exist_ok=True)
    for k, vf in P.items():
        sp.run(["ffmpeg", "-loglevel", "error", "-y", "-i", film, "-filter_complex", f"[0:v:0]{vf}[v]", "-map", "[v]", "-map", "0:a:0?",
                "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                "-movflags", "+faststart", os.path.join(out, k + ".mp4")], check=True)
        sp.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", "2", "-i", os.path.join(out, k + ".mp4"), "-frames:v", "1", os.path.join(out, k + "_thumb.jpg")], check=True)
if __name__ == "__main__": run(*sys.argv[1:3])
