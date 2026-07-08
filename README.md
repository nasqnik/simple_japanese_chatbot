## simple_japanese_chatbot 
**Status**: *in progress*

A tiny CLI Japanese chatbot using the OpenRouter API.
Currently wired model - Google Gemma 4.
The chatbot was created to test different models and different settings, but more on that soon.

### What it does

- **Chat in the terminal**: type a message, get a reply in Japanese.
- **Japanese constraint (best effort)**: tries to use **JLPT N4-level kanji only**; otherwise uses ひらがな / カタカナ (prompt-based, not a strict validator).
- **Basic API error handling**: prints API client errors to stderr and keeps the loop running.

### Requirements

- Python 3.10+ (3.11/3.12 recommended)
- An [OpenRouter](https://openrouter.ai/) API key for the default (cloud) setup (billed in your OpenRouter account, not ChatGPT).

The `openai` line in `requirements.txt` is **only the Python HTTP client** for the same `/v1/chat/completions` JSON shape OpenRouter uses. Chats go to **OpenRouter**, not to OpenAI’s `api.openai.com`, unless you deliberately set `LLM_BASE_URL` to something else.

### Setup

#### 1) Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 2) Install dependencies

```bash
python -m pip install -U pip
pip install -r requirements.txt
```

#### 3) Provide `OPENROUTER_API_KEY`

`chatbot.py` reads `OPENROUTER_API_KEY` from the environment (OpenRouter dashboard).

Option A: export it in your shell (recommended if you don’t want `.env`)

```bash
export OPENROUTER_API_KEY="sk-or-..."
```

Option B: use a `.env` file (this repo gitignores it)

Create `.env`:

```bash
OPENROUTER_API_KEY="sk-or-..."
```

Then run Python with `.env` auto-loaded via `python-dotenv`:

```bash
python -m dotenv run -- python chatbot.py
```

### Run

If you exported `OPENROUTER_API_KEY`:

```bash
python chatbot.py
```

If you’re using `.env`:

```bash
python -m dotenv run -- python chatbot.py
```

Type `exit` / `quit` to stop.

### Local: Tiny Aya Fire (Mac, GGUF + llama.cpp)

Uses [CohereLabs/tiny-aya-fire-GGUF](https://huggingface.co/CohereLabs/tiny-aya-fire-GGUF). **`llama-server`** on your Mac exposes the same **JSON chat API** OpenRouter uses (`/v1/chat/completions`), so the same Python client works—**no cloud, no OpenRouter** while those env vars point at localhost.

1. On Hugging Face, open the GGUF repo and **accept** the model access terms.
2. Install the server: `brew install llama.cpp`
3. Create a **read** token at [HF settings](https://huggingface.co/settings/tokens), then `export HF_TOKEN=hf_...`
4. Start the model: `./scripts/run_tiny_aya_fire.sh` (downloads `tiny-aya-fire-q4_k_m.gguf` under `~/.cache/tiny-aya-fire` on first run).
5. In **another** terminal:

```bash
export LLM_BASE_URL=http://127.0.0.1:8080/v1
export LLM_MODEL=tiny-aya-fire
export LLM_API_KEY=local
python chatbot.py
```

Apple Silicon uses Metal by default (`-ngl 99`). For CPU-only: `N_GPU_LAYERS=0 ./scripts/run_tiny_aya_fire.sh`.

### Project files

- `chatbot.py`: CLI chatbot script
- `scripts/run_tiny_aya_fire.sh`: download GGUF + run `llama-server` for local Tiny Aya Fire
- `requirements.txt`: Python dependencies
- `.env`: your OpenRouter key (ignored by git); not needed for local-only Tiny Aya if you set `LLM_API_KEY=local`

### Troubleshooting

- **`Missing API key` / OpenRouter**
  - You didn’t export `OPENROUTER_API_KEY` in the same terminal session, or
  - You’re using `.env` but you didn’t run with `python -m dotenv run ...`, or
  - For **local Tiny Aya**, unset cloud-only vars and use `LLM_BASE_URL`, `LLM_MODEL`, and `LLM_API_KEY=local` as in the local section above.

- **`AuthenticationError`**
  - The key is wrong/revoked, or your API account/billing isn’t set up.

- **`RateLimitError`**
  - You’re sending too many requests; wait a bit and retry.

- **Connection / 5xx errors**
  - Network hiccup or service issue; retry.