import os
import sys
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
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

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
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=history,
            )
        except (AuthenticationError, 
                RateLimitError,
                APIConnectionError,
                APIStatusError)  as e:
            print(e, file=sys.stderr)
            continue

        bot_text = response.output_text.strip()
        print(f"Bot: {bot_text}\n")
        history.append({"role": "assistant", "content": bot_text})

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Missing OPENAI_API_KEY. Put it in .env or your environment before running.")
    main()