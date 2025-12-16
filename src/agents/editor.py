"""
Agente 1 — Editor: corrige e limpa a transcrição.
"""
import os
from openai import OpenAI


class EditorAgent:
    def __init__(self, client: OpenAI, temperature: float = 0.2):
        self.client = client
        self.temperature = temperature


    def run(self, transcript: str) -> str:
        prompt = f"""
        Você é um especialista em batalhas de rap.


        Tarefa:
        - Reescreva a transcrição abaixo de forma limpa.
        - Corrija palavras erradas, mas respeite linguagem coloquial brasileira e termos em inglês.
        - Mantenha a estrutura de rimas.
        - Não invente nada nem adicione opinião.


        Transcrição original:
        {transcript}


        Retorne APENAS o texto corrigido, sem explicações.
        """.format(transcript=transcript)


        resp = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Você é o AGENTE 1: Editor especialista em batalhas de rap."},
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
        )


        corrected = resp.choices[0].message.content.strip()
        return corrected