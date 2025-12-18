import requests
import re
from pathlib import Path

def escape_markdown_v2(text: str) -> str:
    """
    Escape para Telegram Markdown V2.
    Lista de caracteres a escapar segundo docs: _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    if not isinstance(text, str):
        return text
    # ordem importa — backslash primeiro
    text = text.replace("\\", "\\\\")
    # chars to escape
    chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(chars), r'\\\1', text)

def send_telegram_message(token: str, chat_id: str, text: str,
                          gif_path: str = None,
                          use_markdown: bool = True,
                          disable_web_page_preview: bool = True,
                          timeout: int = 30):
    """
    Envia texto (formatado) e opcionalmente um GIF para Telegram.
    - token: bot token
    - chat_id: id do grupo/canal (ex: -100123...)
    - text: texto final (string)
    - gif_path: caminho local do gif (opcional)
    - use_markdown: se True, usa MarkdownV2 (escape automático). Se False, usa HTML.
    """

    base = f"https://api.telegram.org/bot{token}"

    # prepare text according to parse mode
    if use_markdown:
        parsed_text = text
        parse_mode = "Markdown"
    else:
        # se for HTML, não fazemos escaping automático — cuidado com tags
        parsed_text = text
        parse_mode = "HTML"

    # Primeiro, se houver GIF E caption maior que 1024, envie a mensagem de texto separadamente
    if gif_path:
        caption_limit = 1024
        if len(parsed_text) > caption_limit:
            # envia texto como mensagem normal primeiro
            resp = requests.post(
                f"{base}/sendMessage",
                data={
                    "chat_id": chat_id,
                    "text": parsed_text,
                    "parse_mode": parse_mode,
                    "disable_web_page_preview": str(disable_web_page_preview).lower()
                },
                timeout=timeout
            )
            # log básico
            if resp.status_code != 200:
                print("Erro enviando mensagem:", resp.status_code, resp.text)
        # Agora envia o GIF (com caption se couber)
        files = {}
        with open(gif_path, "rb") as f:
            files = {"animation": f}
            data = {"chat_id": chat_id}
            # se couber como caption, usa; senão usa caption vazio
            if len(parsed_text) <= caption_limit:
                data["caption"] = parsed_text
                data["parse_mode"] = parse_mode
            resp2 = requests.post(
                f"{base}/sendAnimation",
                data=data,
                files=files,
                timeout=timeout
            )
        if resp2.status_code != 200:
            print("Erro enviando GIF:", resp2.status_code, resp2.text)
        else:
            print("GIF enviado com sucesso.")
        return resp2.json()
    else:
        # apenas enviar texto
        resp = requests.post(
            f"{base}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": parsed_text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": str(disable_web_page_preview).lower()
            },
            timeout=timeout
        )
        if resp.status_code != 200:
            print("Erro enviando mensagem:", resp.status_code, resp.text)
        return resp.json()

# EXEMPLO DE USO:
# resp = send_telegram_message(
#     token="1234:ABCD...",
#     chat_id="-1001234567890",
#     text=formatted_text_from_llm,
#     gif_path="data/gifs/batalha.gif",
#     use_markdown_v2=True
# )
# print(resp)
