"""Shared validation and versioned writes. Standard library only."""
import json
import math
import shutil
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text(encoding="utf-8") == text:
            return
        i = 1
        while path.with_name(path.stem + f".previous-{i}" + path.suffix).exists():
            i += 1
        shutil.copy2(path, path.with_name(path.stem + f".previous-{i}" + path.suffix))
    path.write_text(text, encoding="utf-8")


def validate_cuts(cuts, duration):
    result = sorted([float(a), float(b)] for a, b in cuts)
    for i, (a, b) in enumerate(result):
        if not (math.isfinite(a) and math.isfinite(b) and 0 <= a < b <= duration):
            raise ValueError("Cut is outside the source timeline")
        if i and a < result[i - 1][1]:
            raise ValueError("Cuts overlap")
    if sum(b - a for a, b in result) >= duration:
        raise ValueError("Cuts would remove the entire video")
    return result


def validate_words(words, duration):
    if isinstance(words, dict):
        words = words.get("words")
    if not isinstance(words, list) or not words:
        raise ValueError("Expected a non-empty word list with text, start and end")
    result = []
    for i, word in enumerate(words):
        text = word.get("text", word.get("word", "")).strip()
        start, end = float(word["start"]), float(word["end"])
        if not text or not (math.isfinite(start) and math.isfinite(end) and 0 <= start < duration and start < end <= duration + .05):
            raise ValueError(f"Invalid word interval at index {i}")
        if result and start < result[-1]["start"]:
            raise ValueError(f"Word starts are out of order at index {i}")
        result.append(dict(id=i, text=text, start=start, end=min(end, duration)))
    return result
