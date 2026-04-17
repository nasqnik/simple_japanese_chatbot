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

MODEL = "google/gemma-4-26b-a4b-it"
PROVIDER_PREFS = {
    "provider": {
        "order": ["parasail/bf16"],
        "allow_fallbacks": False,
    }
}


def call_chat(client: OpenAI, messages: list[dict]) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        extra_body=PROVIDER_PREFS,
    )
    return resp.choices[0].message.content.strip()

def main():
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("Missing OPENROUTER_API_KEY. Put it in .env or your environment before running.")
    
    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
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
            bot_text = call_chat(client, history)
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