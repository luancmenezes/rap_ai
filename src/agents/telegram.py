import json
from pathlib import Path
from openai import OpenAI


class TelegramFormatAgent:
    """
    Agente que usa LLM para formatar a análise no formato Telegram.

    Em vez de montar o texto em Python, o agente envia
    um prompt à LLM indicando exatamente como deve ser o formato de saída.
    """

    def __init__(self, client):
        self.client = client

    def _build_prompt(self, data: dict) -> str:
        """Constrói o prompt que será enviado ao modelo LLM."""

        return f"""
            Você é um agente de formatação para mensagens de Telegram, usando APENAS Markdown simples no seguinte padrão:

- Negrito: **assim**
- Itálico: __assim__
- Lista: 
  - item 1
  - item 2
- Bloco de poema: colocar entre três crases ``` no início e no fim

NÃO use MarkdownV2 avançado.
NÃO use barras invertidas "\"
NÃO use aspas escapadas.
NÃO use HTML.
NÃO use underline para negrito.
NÃO gere códigos de formatação fora do padrão acima.

Seu objetivo é gerar uma mensagem CURTA, DIRETA, ORGANIZADA e com estilo típico de canal de Telegram.  
As mensagens serão enviadas diretamente para um canal público, então precisam estar visualmente limpas e bonitas.

===============================
DADOS DE ENTRADA
{data}
===============================

### REGRAS DO FORMATO

1. Comece com um título chamativo com emojis em NEGRITO, por exemplo:
   **🔥 BATALHA FINAL — RESUMO 🔥**

2. Depois apresente:
   **MCs Identificados:**
   - Nome 1
   - Nome 2

   **Ordem de Entrada:**
   Descrição curta

   **Observações:**
   Se existirem

3. Em seguida apresente um resumo do contexto da batalha, em 3–5 linhas.

4. Depois liste TODAS as rimas do JSON no formato:
   - "Trecho da rima..."
   - "Trecho da rima..."
   NÃO suprima partes, NÃO coloque reticências que não estão no texto.

5. Se houver poema autoral, apresente assim:

   **Poema:**

            """

    def run(self, data: dict) -> str:
        prompt = self._build_prompt(data)

        response = self.client.responses.create(
            model="gpt-4.1",
            input=prompt
        )

        return response.output_text