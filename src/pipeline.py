import json
import os
from src.download_video import download_youtube
from src.download_gif import generate_gif_from_youtube
from src.transcribe import transcribe
from src.trancribe_openai import transcribe
from src.analyze_llm import analyze_with_llm
from src.generate_html import generate_html
from openai import OpenAI
from src.agents.editor import EditorAgent
from src.agents.mc_identifier import MCIdentifierAgent
from src.agents.punchline_analyzer import PunchlineAnalyzerAgent
from src.agents.telegram import TelegramFormatAgent
from src.telegram import send_telegram_message
from pathlib import Path
from datetime import datetime

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Sete sua OPENAI_API_KEY no .env ou ambiente.")

TELEGRAM_BOT_TOKEN = "8487276319:AAGOthzO0iGsQOF_vItOmnxBTYRiRwTC0K0"
TELEGRAM_CHAT_ID = -1003436035299
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "data/outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

client = OpenAI(api_key=OPENAI_API_KEY)

# instanciar agentes
editor = EditorAgent(client)
mc_identifier = MCIdentifierAgent(client)
analyzer = PunchlineAnalyzerAgent(client)
telegram = TelegramFormatAgent(client)

class Pipeline:
    def __init__(self, url = None, transcript_path = None):
        self.url = url
        self.audio_dir = "data/raw_audio"
        self.transcript_path = transcript_path
        self.analysis = None
        self.output_path = None
        self._run()

    def _run(self):
        #print("🔽 Baixando áudio...")
        #download_youtube(self.url)
        print("Gerando GIF")
        generate_gif_from_youtube(self.url)
        audio = self._pick_latest_audio()

        print("🎙️ Transcrevendo...")
        self.transcript_path = transcribe(audio)
        with open(self.transcript_path, "r") as handle:
            transcript = handle.read()

        print("🧠 Rodando LLM...")
        # Agente 1
        corrected = editor.run(transcript)
        print("[supervisor] transcrição corrigida")
        # Agente 2
        mcs = mc_identifier.run(corrected)
        print("[supervisor] MCs identificados", mcs)


        # Agente 3
        analysis = analyzer.run(corrected, mcs)
        print("[supervisor] análise de punchlines obtida")
        final = {
            "transcricao_corrigida": corrected,
            "mcs": mcs,
            "analise": analysis,
            "meta": {
            "timestamp": datetime.now().isoformat(),
            }
        }
        msg_telegram = telegram.run(final)
        final["telegram"] = msg_telegram

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
            use_markdown_v2=True
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
