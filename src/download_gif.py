import subprocess
import os
import tempfile
from pathlib import Path

def download_video_fragment(url: str, output_path: str, duration: int = 80):
    """
    Baixa apenas os primeiros <duration> segundos do vídeo
    para economizar banda. Útil pois não precisamos do vídeo inteiro.
    """
    cmd = [
        "yt-dlp",
        "--quiet",
        "--no-warnings",
        "-f", "mp4",
        "--download-sections", f"*0-{duration}",
        "-o", output_path,
        url,
    ]
    subprocess.run(cmd, check=True)


def generate_battle_gif(video_path: str, output_path: str):
    """
    Cria um GIF de ~10 segundos combinando:
    - 4s do início
    - 6s do meio do vídeo

    Saída final: GIF pronto para Telegram.
    """

    # Arquivos temporários
    temp_dir = tempfile.mkdtemp()
    clip1 = f"{temp_dir}/clip_start.mp4"
    clip2 = f"{temp_dir}/clip_mid.mp4"
    merged = f"{temp_dir}/merged.mp4"

    # --- descobrir duração do vídeo ---
    probe_cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of",
        "default=noprint_wrappers=1:nokey=1", video_path
    ]
    duration = float(subprocess.check_output(probe_cmd).decode().strip())

    mid_start = max(0, duration * 0.5 - 3)  # pega um trecho centrado

    # --- 4 segundos do início ---
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-ss", "0", "-t", "4",
        "-vf", "scale=480:-1,fps=12",
        clip1
    ], check=True)

    # --- 6 segundos do meio ---
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-ss", str(mid_start), "-t", "6",
        "-vf", "scale=480:-1,fps=12",
        clip2
    ], check=True)

    # --- concatenar os clipes ---
    concat_list = f"{temp_dir}/list.txt"
    Path(concat_list).write_text(f"file '{clip1}'\nfile '{clip2}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c", "copy", merged
    ], check=True)

    # --- gerar GIF ---
    subprocess.run([
        "ffmpeg", "-y",
        "-i", merged,
        "-vf", "fps=12,scale=480:-1:flags=lanczos",
        output_path
    ], check=True)

    return output_path


def generate_gif_from_youtube(url: str, output_dir="data/gifs"):
    """
    Função principal:
    1. Baixa apenas o início do vídeo (otimizado)
    2. Gera o GIF final com 10s
    """

    os.makedirs(output_dir, exist_ok=True)

    temp_video = f"{output_dir}/temp_fragment.mp4"
    final_gif = f"{output_dir}/gif_batalha.gif"

    print("🔽 Baixando fragmento do vídeo...")
    download_video_fragment(url, temp_video)

    print("🎞️ Gerando GIF...")
    generate_battle_gif(temp_video, final_gif)

    print(f"🎉 GIF pronto: {final_gif}")
    return final_gif
