"""Token counting shared by chunking and (later) context-budget management.

Uses tiktoken's cl100k_base (the tokenizer for OpenAI's text-embedding-3 models).
For Claude it is only an approximation, which is fine for budgeting. tiktoken
downloads its vocabulary on first use; if that fails (offline, firewall), we fall
back to a ~4 characters-per-token estimate instead of crashing.
"""

from functools import lru_cache

CHARS_PER_TOKEN = 4


@lru_cache(maxsize=1)
def _enc():
    try:
        import tiktoken

        return tiktoken.get_encoding("cl100k_base")
    except Exception as e:  # network/proxy errors surface as various types
        print(f"[tokens] tiktoken unavailable ({type(e).__name__}); using char estimate")
        return None


def count_tokens(text: str) -> int:
    enc = _enc()
    if enc is None:
        return max(1, len(text) // CHARS_PER_TOKEN)
    return len(enc.encode(text))


def truncate_tokens(text: str, max_tokens: int) -> str:
    enc = _enc()
    if enc is None:
        return text[: max_tokens * CHARS_PER_TOKEN]
    ids = enc.encode(text)
    return text if len(ids) <= max_tokens else enc.decode(ids[:max_tokens])
