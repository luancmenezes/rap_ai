"""
Agente 2 — Identificador de MCs
"""
import json
from openai import OpenAI


class MCIdentifierAgent:
    def __init__(self, client: OpenAI, temperature: float = 0.2):
        self.client = client
        self.temperature = temperature


    def run(self, corrected_transcript: str) -> dict:

        prompt = f"""
        Você é o AGENTE 2: Identificador de MCs em batalhas de rap.


        Com base na transcrição corrigida abaixo, identifique:
        - Nome dos MCs envolvidos.
        - Quem começa.
        - Quem responde.
        - Como você inferiu isso (breve explicação).


        Transcrição corrigida:
        {corrected_transcript}


        Retorne em JSON com as chaves: mcs (lista), ordem_entrada (string), observacoes (string).
        """.format(corrected_transcript=corrected_transcript)


        resp = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Você é o AGENTE 2: Identificador de MCs."},
                {"role": "user", "content": prompt},
                ],
            temperature=self.temperature,
        )


        raw = resp.choices[0].message.content
        # tentar encontrar json embutido
        try:
            data = json.loads(raw)
        except Exception:
            # tentar extrair bloco JSON
            start = raw.find('{')
            end = raw.rfind('}')
            if start == -1 or end == -1:
                raise ValueError('AGENTE 2 não retornou JSON válido')
            data = json.loads(raw[start:end+1])


        return data