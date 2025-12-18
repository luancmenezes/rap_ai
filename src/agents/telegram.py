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
            Você é um agente de formatação de mensagens para Telegram.

                    ⚠️ IMPORTANTE:
                    - O texto será enviado via API usando parse_mode = "Markdown" (LEGACY).
                    - Use APENAS Markdown simples compatível com Telegram LEGACY.
                    - Gere texto que funcione IGUAL ao envio manual no app do Telegram.

                    ===============================
                    REGRAS DE FORMATAÇÃO (OBRIGATÓRIAS)
                    ===============================

                    - Negrito: **assim**
                    - Itálico: __assim__
                    - Lista:
                    - item 1
                    - item 2
                    - Bloco de poema: usar exatamente três crases ``` no início e no fim

                    ===============================
                    PROIBIÇÕES ABSOLUTAS
                    ===============================

                    - NÃO usar MarkdownV2
                    - NÃO usar barras invertidas "\" em nenhum contexto
                    - NÃO escapar caracteres
                    - NÃO usar HTML
                    - NÃO usar underline para negrito
                    - NÃO misturar padrões de Markdown
                    - NÃO gerar símbolos de formatação fora do padrão acima

                    ===============================
                    OBJETIVO
                    ===============================

                    Gerar uma mensagem:
                    - CURTA
                    - DIRETA
                    - ORGANIZADA
                    - Visualmente LIMPA
                    - Com estilo típico de CANAL DE TELEGRAM

                    O texto será publicado em um canal público.

                    ===============================
                    ESTRUTURA OBRIGATÓRIA DA MENSAGEM
                    ===============================

                    1. Comece com um título chamativo em NEGRITO com emojis.
                    Exemplo:
                    **🔥 BATALHA FINAL — RESUMO 🔥**

                    2. Em seguida, apresente exatamente nesta ordem:

                    **MCs Identificados:**
                    - Nome 1
                    - Nome 2

                    **Ordem de Entrada:**
                    Descrição curta e objetiva

                    **Observações:**
                    Apenas se existirem

                    3. Depois, escreva um resumo do contexto da batalha em 3 a 5 linhas curtas.

                    4. Em seguida, liste TODAS as rimas recebidas nos dados de entrada, no formato:
                    - "Trecho da rima exatamente como recebido"
                    - "Outro trecho exatamente como recebido"

                    ⚠️ Regras:
                    - NÃO remover partes
                    - NÃO resumir
                    - NÃO adicionar reticências
                    - NÃO reinterpretar o texto

                    5. Se houver poema autoral, apresente exatamente assim:

                    **Poema:**

                    ===============================
                    DADOS DE ENTRADA
                    ===============================
                    {data}
                    ===============================
                """

    def run(self, data: dict) -> str:
        prompt = self._build_prompt(data)

        response = self.client.responses.create(
            model="gpt-4.1",
            input=prompt
        )

        return response.output_text