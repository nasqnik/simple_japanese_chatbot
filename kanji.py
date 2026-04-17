def load_kanji_whitelist(path: str) -> set[str]:
    allowed = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            allowed.update(list(line))
    return allowed

def is_kanji(ch: str) -> bool:
    return "\u4e00" <= ch <= "\u9fff"
    
def find_disallowed_kanji(text: str, allowed: set[str]) -> set[str]:
    return {ch for ch in text if is_kanji(ch) and ch not in allowed}