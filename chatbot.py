"""
CLI chatbot: HTTP calls go to OpenRouter (cloud) or to llama.cpp on this machine (local).

Uses the third-party `openai` Python package only as a client for the common
`/v1/chat/completions` JSON API. That is the same wire format OpenRouter exposes;
it does not send traffic to OpenAI's api.openai.com unless you point LLM_BASE_URL there.
"""
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    RateLimitError,
)

from kanji import load_kanji_whitelist, find_disallowed_kanji

SYSTEM_PROMPT = """あなたは日本語の会話パートナーです。あかるく、フレンドリーに、たくさん会話を広げてください。
基本は日本語で答えてください（ユーザーが英語なら、かんたんな日本語+短い英語でOK）。

## ルール
- へんじは「チャットっぽく」します（あいづち、かんたんなかんそう、しつもんでつづける）。
- ながすぎない。ひつようなら1文でもOK。ふつうは1〜4文くらい。
- むずかしいことばは、やさしいことばに言いかえる。

## かんじ
- かんじはN4までをできるだけ使う（ぜんぶひらがなだけにしない）。
- つかってよいかんじのれい: 私、今、日、時、分、行、来、見、食、飲、話、友、好、学、買、出、入、先、週、前、後、休
- N4より上のかんじは使わない。じしんがないときは、ひらがな/カタカナにする。

## まちがいのなおし（みじかく）
- ユーザーの文にまちがいがあれば、へんじの最後に「なおし: ...」を1つだけつける。
- なおしはみじかく。ぜんぶなおさない（いちばん大事な1つだけ）。
"""

DEFAULT_OPENROUTER_URL = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODEL = "google/gemma-4-26b-a4b-it"

PROVIDER_PREFS = {
    "provider": {
        "order": ["parasail/bf16"],
        "allow_fallbacks": False,
    }
}


def _is_local_llm_url(url: str) -> bool:
    u = url.lower().split("://", 1)[-1]
    return u.startswith("127.0.0.1") or u.startswith("localhost")


def call_chat(client: OpenAI, messages: list[dict], *, model: str, use_parasail_prefs: bool) -> str:
    kwargs: dict = {"model": model, "messages": messages}
    if use_parasail_prefs:
        kwargs["extra_body"] = PROVIDER_PREFS
    resp = client.chat.completions.create(**kwargs)
    content = resp.choices[0].message.content
    return (content or "").strip()

def main():
    load_dotenv()
    base_url = os.getenv("LLM_BASE_URL", DEFAULT_OPENROUTER_URL).rstrip("/")
    model = os.getenv("LLM_MODEL", DEFAULT_OPENROUTER_MODEL)
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        if _is_local_llm_url(base_url):
            api_key = "local"
        else:
            raise SystemExit(
                "Missing API key. Set OPENROUTER_API_KEY for OpenRouter, "
                "or run Tiny Aya locally: LLM_BASE_URL=http://127.0.0.1:8080/v1 and LLM_API_KEY=local "
                "(see scripts/run_tiny_aya_fire.sh)."
            )

    use_parasail_prefs = (
        "openrouter.ai" in base_url
        and "gemma" in model.lower()
        and os.getenv("LLM_OPENROUTER_PARASAIL", "1") not in {"0", "false", "no"}
    )

    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    print("Hi. I'm your Japanese-exchange friend 🇯🇵")
    print("Type your first sentence in Japanese and I'll switch to Japanese")
    print("or type 'exit' to quit 🌸")

    allowed_kanji = load_kanji_whitelist("data/jlpt_with_n4_kanji.txt")
    
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    while True:
        user_text = input("You: ").strip()
        if not user_text:
            continue
        if user_text.lower() in {"exit", "quit"}:
            break

        history.append({"role": "user", "content": user_text})

        try:
            bot_text = call_chat(client, history, model=model, use_parasail_prefs=use_parasail_prefs)
        except (AuthenticationError, 
                RateLimitError,
                APIConnectionError,
                APIStatusError)  as e:
            print(e, file=sys.stderr)
            continue

        bad = find_disallowed_kanji(bot_text, allowed_kanji)
        if bad:
            rewrite_prompt = (
                "つぎのテキストを、できるだけそのままにして、"
                "「だめな かんじ」にある文字だけを ひらがな/カタカナ におきかえてください。"
                "それいがいの文字（かな、かんじ、きごう、くうはく、かいぎょう、えもじ）は ぜったいに かえないでください。"
                "せつめいは いらない。へんこうごのテキストだけを出力して。\n"
                f"だめな かんじ: {''.join(sorted(bad))}\n"
                f"テキスト: {bot_text}"
            )

            try:
                bot_text = call_chat(
                    client,
                    [{"role": "user", "content": rewrite_prompt}],
                    model=model,
                    use_parasail_prefs=use_parasail_prefs,
                )
            except (AuthenticationError, 
                    RateLimitError,
                    APIConnectionError,
                    APIStatusError)  as e:
                print(e, file=sys.stderr)
                continue

        print(f"Bot: {bot_text}")
        history.append({"role": "assistant", "content": bot_text})

if __name__ == "__main__":
    main()