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

SYSTEM_PROMPT = """
あなたは親切で簡潔な日本語チャットボットです。基本的に日本語で答えてください。
漢字は日本語能力試験N4レベルまでのものだけを使ってください。N4より上の漢字は使わず、ひらがなかカタカナで書いてください。
むずかしいことばは、やさしいことばに言いかえてください。
"""

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
    
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    while True:
        user_text = input("You: ").strip()
        if not user_text:
            continue
        if user_text.lower() in {"exit", "quit"}:
            break

        history.append({"role": "user", "content": user_text})

        try:
            response = client.chat.completions.create(
                model="google/gemma-4-26b-a4b-it",
                messages=history,
                extra_body={
                    "provider" : {
                        "order" : ["parasail/bf16"],
                        "allow_fallbacks": False,
                    }
                }
            )
        except (AuthenticationError, 
                RateLimitError,
                APIConnectionError,
                APIStatusError)  as e:
            print(e, file=sys.stderr)
            continue

        bot_text = response.choices[0].message.content.strip()
        print(f"Bot: {bot_text}")
        history.append({"role": "assistant", "content": bot_text})

if __name__ == "__main__":
    main()