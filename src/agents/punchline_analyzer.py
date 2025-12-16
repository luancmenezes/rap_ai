"""
Agente 3 — Analista de punchlines (usa template em prompts/poetry_extract.txt)
"""
import json
from pathlib import Path
from openai import OpenAI


class PunchlineAnalyzerAgent:
    def __init__(self, client: OpenAI, template_path: str = "prompts/poetry_extract.txt", temperature: float = 0.3):
        self.client = client
        self.template_path = template_path
        self.temperature = temperature


    def run(self, corrected_transcript: str, mcs_data: dict) -> dict:
        template = Path(self.template_path).read_text(encoding="utf-8")
        filled = template.replace("{{transcricao}}", corrected_transcript)
        filled = filled.replace("{{mcs_json}}", json.dumps(mcs_data, ensure_ascii=False))


        resp = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
            {"role": "system", "content": "Você é o AGENTE 3: Analista de punchlines e impacto lírico."},
            {"role": "user", "content": filled},
            ],
            temperature=self.temperature,
        )


        raw = resp.choices[0].message.content
        # extrair bloco JSON
        start = raw.find('{')
        end = raw.rfind('}')
        if start == -1 or end == -1 or end <= start:
            raise ValueError('O AGENTE 3 não retornou JSON válido.')


        return json.loads(raw[start:end+1])