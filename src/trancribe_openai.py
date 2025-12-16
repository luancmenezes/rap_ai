import os
from pathlib import Path
from openai import OpenAI

BASE_DIR = Path("/Users/luanmenezes/Documents/personal_projects/rap_llm")
TRANSCRIPTS_DIR = BASE_DIR / "data" / "transcripts"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt = """
Você é um transcritor especializado em batalhas de rima, saiba que os mcs usam também termos ingles como, flow, nigga, brother, hip hop, etc

Transcreva o áudio com:
- timestamp por linha
- formato [MM:SS]
- texto limpo e sem ruído

Exemplo desejado:
[00:12]: Eu chego firme, mandando o meu flow com rima e batida.
[00:18]: Pode vir quente que eu tô fervendo na missão.
[00:22]: Meu verso é faca afiada cortando a competição.

IMPORTANTE:
- Sempre coloque o timestamp.
- Nunca junte duas falas com timestamps diferentes.
"""


def transcribe(mp3_path: str) -> str:
    """
    Transcribe an MP3 audio file using OpenAI's transcription API.
    
    Args:
        mp3_path: Path to the MP3 file to transcribe
        
    Returns:
        Path to the saved transcription file
    """
    audio_path = Path(mp3_path)
    
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {mp3_path}")
    
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = TRANSCRIPTS_DIR / (audio_path.stem + ".txt")
    
    with audio_path.open("rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file,
            prompt=prompt,
            response_format="text"
        )
    
    output_path.write_text(transcription, encoding="utf-8")
    
    print("\nArquivo salvo em:", output_path)
    
    return str(output_path)

