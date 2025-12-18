import json
import os
from pathlib import Path
from datetime import datetime

from src.download_video import download_youtube
from src.download_gif import generate_gif_from_youtube
from src.transcribe import transcribe
from src.trancribe_openai import transcribe
from src.telegram import send_telegram_message
from src.langchain_pipeline import run_langchain_rap_pipeline

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Sete sua OPENAI_API_KEY no .env ou ambiente.")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") 
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "data/outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class Pipeline:
    def __init__(self, url = None, transcript_path = None):
        self.url = url
        self.audio_dir = "data/raw_audio"
        self.transcript_path = transcript_path
        self.analysis = None
        self.output_path = None
        self._run()

    def _run(self):
        print("🔽 Baixando áudio...")
        download_youtube(self.url)
        print("Gerando GIF")
        generate_gif_from_youtube(self.url)
        audio = self._pick_latest_audio()

        print("🎙️ Transcrevendo...")
        self.transcript_path = transcribe(audio)
        with open(self.transcript_path, "r") as handle:
            transcript = handle.read()

        print("🧠 Rodando pipeline LangChain...")
        lc_result = run_langchain_rap_pipeline(transcript)
        final = lc_result.to_dict()
        msg_telegram = final["telegram"]

        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        analysis_path = Path(OUTPUT_DIR) / f"analysis_{timestamp}.json"
        telegram_path = Path(OUTPUT_DIR) / f"telegram_{timestamp}.txt"

        with open(analysis_path, "w", encoding="utf-8") as handle:
            json.dump(final, handle, ensure_ascii=False, indent=2)
        with open(telegram_path, "w", encoding="utf-8") as handle:
            handle.write(msg_telegram)

        self.output_path = str(analysis_path)

        print("[supervisor] outputs salvos em", analysis_path, "e", telegram_path)
        print("Pronto! Arquivo gerado em:", self.output_path)
        send_telegram_message(
            token=TELEGRAM_BOT_TOKEN,
            chat_id=TELEGRAM_CHAT_ID,   # canal, grupo ou pessoa
            text=msg_telegram,
            gif_path="/Users/luanmenezes/Documents/personal_projects/rap_llm/data/gifs/gif_batalha.gif",
            use_markdown=True
        )
    def _pick_latest_audio(self):
        candidates = sorted(
            (os.path.join(self.audio_dir, f) for f in os.listdir(self.audio_dir)),
            key=os.path.getmtime,
            reverse=True,
        )
        if not candidates:
            raise FileNotFoundError(
                f"Nenhum áudio encontrado em {self.audio_dir}. Baixe um vídeo primeiro."
            )
        return candidates[0]
