#!/usr/bin/env bash
# Run Tiny Aya Fire (GGUF) locally on macOS with llama.cpp (Metal on Apple Silicon).
# llama-server speaks the same /v1/chat/completions JSON as OpenRouter (not OpenAI Inc).
#
# 1) One-time: accept the model terms on Hugging Face:
#    https://huggingface.co/CohereLabs/tiny-aya-fire-GGUF
# 2) Create a read token: https://huggingface.co/settings/tokens
# 3) brew install llama.cpp
# 4) export HF_TOKEN=hf_...
# 5) ./scripts/run_tiny_aya_fire.sh
#
# In another terminal (same machine):
#   export LLM_BASE_URL=http://127.0.0.1:8080/v1
#   export LLM_MODEL=tiny-aya-fire
#   export LLM_API_KEY=local
#   python chatbot.py
#
# Optional: PORT=9000 TINY_AYA_CACHE=~/my-models ./scripts/run_tiny_aya_fire.sh
# Intel Mac / CPU-only: set N_GPU_LAYERS=0

set -euo pipefail

LLAMA_SERVER=""
for name in llama-server llama-cpp-server; do
  if command -v "${name}" &>/dev/null; then
    LLAMA_SERVER="$(command -v "${name}")"
    break
  fi
done
if [[ -z "${LLAMA_SERVER}" ]]; then
  echo "Missing llama-server. Install with:  brew install llama.cpp" >&2
  exit 1
fi

if [[ -z "${HF_TOKEN:-}" ]]; then
  echo "Set HF_TOKEN to a Hugging Face read token (and accept the GGUF repo license in the browser)." >&2
  exit 1
fi

CACHE="${TINY_AYA_CACHE:-${HOME}/.cache/tiny-aya-fire}"
GGUF_NAME="tiny-aya-fire-q4_k_m.gguf"
HF_URL="https://huggingface.co/CohereLabs/tiny-aya-fire-GGUF/resolve/main/${GGUF_NAME}"
PORT="${PORT:-8080}"
N_GPU_LAYERS="${N_GPU_LAYERS:-99}"

mkdir -p "${CACHE}"
DEST="${CACHE}/${GGUF_NAME}"

if [[ ! -f "${DEST}" ]]; then
  echo "Downloading ${GGUF_NAME} to ${DEST} ..." >&2
  curl -fL --progress-bar \
    -H "Authorization: Bearer ${HF_TOKEN}" \
    -o "${DEST}.partial" \
    "${HF_URL}"
  mv "${DEST}.partial" "${DEST}"
fi

echo "Starting llama-server on http://127.0.0.1:${PORT} (Ctrl+C to stop) ..." >&2
exec "${LLAMA_SERVER}" \
  -m "${DEST}" \
  --host 127.0.0.1 \
  --port "${PORT}" \
  --jinja \
  -ngl "${N_GPU_LAYERS}"
