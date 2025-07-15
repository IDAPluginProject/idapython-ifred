from typing import List, Tuple

def fuzzy_match_simple(pattern: str, string: str) -> bool:
    if not pattern:
        return True

    pattern_idx = 0
    for c in string:
        if pattern[pattern_idx].lower() == c.lower():
            pattern_idx += 1
            if pattern_idx >= len(pattern):
                break

    return pattern_idx >= len(pattern)
