import unicodedata
import subprocess
import re
import os

def sanitize_filename(name):
    # remove acentos
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    # troca caracteres estranhos por _
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
    return name

def transcribe(audio_file, output_dir="data/transcripts"):
    os.makedirs(output_dir, exist_ok=True)

    # cria nome seguro
    base = os.path.basename(audio_file)
    safe = sanitize_filename(base)
    safe_path = os.path.join(os.path.dirname(audio_file), safe)

    # renomeia
    if safe != base:
        os.rename(audio_file, safe_path)
        audio_file = safe_path
    
    cmd = [
        "whisper",
        audio_file,
        "--model", "large-v3",
        "--language", "pt",
        "--output_dir", output_dir
    ]

    subprocess.run(cmd)

    # retorna caminho TXT
    return os.path.join(output_dir, safe.replace(".mp3", ".txt"))
