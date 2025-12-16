import json
import os
from datetime import datetime
from openai import OpenAI


def analyze_with_llm(
    transcript,
    prompt_file="prompts/poetry_extract.txt",
    output_dir="data/outputs",
):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # -------------------------------------------------
    # AGENTE 1 — CORRIGIR TRANSCRIÇÃO
    # -------------------------------------------------
    agent1_prompt = f"""
    Você é um especialista em batalhas de rap.

    Tarefa:
    - Reescreva a transcrição abaixo de forma limpa.
    - Corrija palavras erradas, mas saiba que é utilizado linguagem e coloquial brasileira.
    - Além disso os MCs algumas vezes utilizam palavra em ingles, como nome de artistas no RAP americano, nomes como punch, puchline, nigga e outros.
    - Mantenha a estrutura de rimas.
    - Não invente nada.
    - Não adicione opinião.

    Transcrição original:
    {transcript}

    Retorne APENAS o texto corrigido, sem explicações.
    """

    agent1_response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Você é o AGENTE 1: Editor especialista em batalhas de rap."},
            {"role": "user", "content": agent1_prompt},
        ],
        temperature=0.2,
    )

    corrected_transcript = agent1_response.choices[0].message.content.strip()

    # -------------------------------------------------
    # AGENTE 2 — IDENTIFICAR MCs
    # -------------------------------------------------
    agent2_prompt = f"""
Você é o AGENTE 2: Identificador de MCs em batalhas de rap.

Com base na transcrição corrigida abaixo, identifique:

- Nome dos MCs envolvidos.
- Quem começa.
- Quem responde.
- Como você inferiu isso (contexto de chamada, vocativos, estilo).

Transcrição corrigida:
{corrected_transcript}

Retorne em JSON:
{{
  "mcs": ["MC1", "MC2"],
  "ordem_entrada": "MC1 começa, MC2 responde",
  "observacoes": "Explicação curta de como identificou"
}}
"""

    agent2_response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Você é o AGENTE 2: Identificador de MCs."},
            {"role": "user", "content": agent2_prompt},
        ],
        temperature=0.2,
    )

    agent2_json_raw = agent2_response.choices[0].message.content
    # garantir json
    mcs_data = json.loads(agent2_json_raw)

    # -------------------------------------------------
    # AGENTE 3 — ANÁLISE DE PUNCHLINES
    # (usa template do seu prompt_file)
    # -------------------------------------------------
    with open(prompt_file, "r") as handle:
        template = handle.read()

    filled_prompt = template.replace("{{transcricao}}", corrected_transcript)

    filled_prompt = template.replace("{{Nome dos MCs}}", agent2_json_raw)
    agent3_response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Você é o AGENTE 3: Analista de punchlines e impacto lírico."},
            {"role": "user", "content": filled_prompt},
        ],
        temperature=0.3,
    )

    raw_out_agent3 = agent3_response.choices[0].message.content

    # extrair JSON final
    start = raw_out_agent3.find("{")
    end = raw_out_agent3.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("O AGENTE 3 não retornou JSON válido.")

    punch_data = json.loads(raw_out_agent3[start : end + 1])

    # -------------------------------------------------
    # OUTPUT FINAL MANTENDO SEU PIPELINE
    # -------------------------------------------------
    final_data = {
        "transcricao_corrigida": corrected_transcript,
        "mcs": mcs_data,
        "analise": punch_data,
    }

    # salvar raw como antes
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_path = os.path.join(output_dir, f"analysis_{timestamp}_raw.txt")

    with open(raw_path, "w") as handle:
        handle.write(json.dumps(final_data, ensure_ascii=False, indent=2))

    return final_data
