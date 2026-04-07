## simple_japanese_chatbot 
**Status**: *in progress*

A tiny CLI Japanese chatbot using the OpenRouter API.
Currently wired model - Google Gemma 4.
The chatbot was created to test different models and different settings, but more on that soon.

### What it does

- **Chat in the terminal**: type a message, get a reply in Japanese.
- **Japanese constraint (best effort)**: tries to use **JLPT N4-level kanji only**; otherwise uses ひらがな / カタカナ (prompt-based, not a strict validator).
- **Basic API error handling**: prints OpenAI SDK exceptions to stderr and keeps the loop running.

### Requirements

- Python 3.10+ (3.11/3.12 recommended)
- An OpenAI API key (billed separately from ChatGPT subscriptions)

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

#### 3) Provide `OPENAI_API_KEY`

Your script reads `OPENAI_API_KEY` from the environment.

Option A: export it in your shell (recommended if you don’t want `.env`)

```bash
export OPENAI_API_KEY="sk-..."
```

Option B: use a `.env` file (this repo gitignores it)

Create `.env`:

```bash
OPENAI_API_KEY="sk-..."
```

Then run Python with `.env` auto-loaded via `python-dotenv`:

```bash
python -m dotenv run -- python chatbot.py
```

### Run

If you exported `OPENAI_API_KEY`:

```bash
python chatbot.py
```

If you’re using `.env`:

```bash
python -m dotenv run -- python chatbot.py
```

Type `exit` / `quit` to stop.

### Project files

- `chatbot.py`: CLI chatbot script
- `requirements.txt`: Python dependencies
- `.env`: your API key (ignored by git)

### Troubleshooting

- **`Missing OPENAI_API_KEY`**
  - You didn’t export the variable in the same terminal session, or
  - You’re using `.env` but you didn’t run with `python -m dotenv run ...`, or
  - The variable name is not exactly `OPENAI_API_KEY`.

- **`AuthenticationError`**
  - The key is wrong/revoked, or your API account/billing isn’t set up.

- **`RateLimitError`**
  - You’re sending too many requests; wait a bit and retry.

- **Connection / 5xx errors**
  - Network hiccup or service issue; retry.