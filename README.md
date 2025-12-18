## rap_ai — RAP LLM Pipeline (LangChain)

Projeto para analisar batalhas de RAP (YouTube) usando LLMs.  
Agora o pipeline principal usa **LangChain** para orquestrar os passos de LLM.

### Visão geral

- **Download / GIF**: baixa o áudio do YouTube e gera um GIF (`download_video`, `download_gif`).
- **Transcrição**: converte o áudio em texto (`transcribe`).
- **Pipeline LangChain**: corrige a transcrição, identifica MCs, analisa punchlines e gera mensagem para Telegram (`langchain_pipeline`).
- **Envio Telegram**: manda texto + GIF para o canal/grupo (`telegram`).

Arquivos principais:

- `src/pipeline.py`: pipeline “supervisor” que coordena tudo e chama o pipeline LangChain.
- `src/langchain_pipeline.py`: implementação com LangChain (LLMs, prompts e parsing).
- `run_pipeline.py`: CLI simples para rodar tudo a partir de uma URL do YouTube.

### Setup do ambiente

```bash
conda env create -f environment.yml
conda activate rapllm
```

Defina a `OPENAI_API_KEY` no ambiente (ou em um `.env` que você mesmo carregue antes):

```bash
export OPENAI_API_KEY="seu_token_aqui"
```

Opcional: defina diretório de saída (senão usa `data/outputs`):

```bash
export OUTPUT_DIR="data/outputs"
```

### Rodando o pipeline completo (CLI)

Com o ambiente ativado e `OPENAI_API_KEY` setada:

```bash
python run_pipeline.py "https://www.youtube.com/watch?v=ID_DO_VIDEO"
```

Isso irá:

- Baixar o vídeo/áudio (se você descomentar o download no `Pipeline`).
- Gerar o GIF da batalha.
- Transcrever o áudio.
- Rodar o **pipeline LangChain** (`run_langchain_rap_pipeline`) em `src/langchain_pipeline.py`.
- Salvar:
  - JSON de análise em `data/outputs/analysis_YYYYMMDDTHHMMSS.json`
  - Texto formatado para Telegram em `data/outputs/telegram_YYYYMMDDTHHMMSS.txt`
- Enviar a mensagem + GIF para o Telegram com `src/telegram.py`.

### Usando o pipeline LangChain direto em Python

Se quiser chamar somente a parte de LLM (sem download/transcrição), você pode usar:

```python
from pathlib import Path
from src.langchain_pipeline import run_langchain_rap_pipeline

transcript = Path("data/transcripts/alguma_batalha.txt").read_text(encoding="utf-8")
result = run_langchain_rap_pipeline(transcript)

final_dict = result.to_dict()
print(final_dict["telegram"])
```

`result.to_dict()` retorna:

- `transcricao_corrigida`
- `mcs` (dict com MCs, ordem de entrada, observações)
- `analise` (JSON da análise de punchlines)
- `telegram` (texto pronto para Telegram)
- `meta` (inclui timestamp e engine = "langchain")

### Comandos básicos (resumo)

- **Criar/ativar ambiente**:

```bash
conda env create -f environment.yml
conda activate rapllm
export OPENAI_API_KEY="seu_token_aqui"
```

- **Rodar pipeline completo a partir de uma URL**:

```bash
python run_pipeline.py "https://www.youtube.com/watch?v=ID_DO_VIDEO"
```

- **Testar somente a parte LangChain com uma transcrição pronta (em Python REPL)**:

```python
from pathlib import Path
from src.langchain_pipeline import run_langchain_rap_pipeline

txt = Path("caminho/para/transcricao.txt").read_text(encoding="utf-8")
res = run_langchain_rap_pipeline(txt)
print(res.telegram)
```

