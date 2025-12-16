import subprocess
import os

def download_youtube(url, output_dir="data/raw_audio"):
    os.makedirs(output_dir, exist_ok=True)
    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "-o", f"{output_dir}/%(title)s.%(ext)s",
        url
    ]
    subprocess.run(cmd)
