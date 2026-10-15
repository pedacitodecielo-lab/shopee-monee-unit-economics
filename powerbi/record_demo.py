"""Turn the raw window capture (record_window.py) into the demo video and a GIF preview.

usage: python record_demo.py x y w h   -> images/shopee_monee_demo.mp4 (1280 px wide) + images/shopee_monee_demo.gif
x y w h = the report canvas inside video/window_raw.mp4 (drops the Power BI ribbon and side panes).
Uses the ffmpeg binary bundled with imageio-ffmpeg.
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
OUT = Path(__file__).parent / "video"
IMG = Path(__file__).parent.parent / "images"

x, y, w, h = sys.argv[1:5]
subprocess.run([FF, "-y", "-i", str(OUT / "window_raw.mp4"), "-vf", f"crop={w}:{h}:{x}:{y},scale=1280:-2:flags=lanczos",
                "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an",
                str(IMG / "shopee_monee_demo.mp4")], check=True)
subprocess.run([FF, "-y", "-i", str(IMG / "shopee_monee_demo.mp4"), "-vf",
                "fps=5,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];[b][p]paletteuse=dither=none:diff_mode=rectangle",
                str(IMG / "shopee_monee_demo.gif")], check=True)
