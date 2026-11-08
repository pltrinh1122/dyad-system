#!/usr/bin/env python3
"""Fixed-set similarity (core script; d-work #642; the decision criterion `dyad/dmc/judgement-complexity.jsonld` names
when a decision may be derived by it). Kernel: Python 3.12+, stdlib only.
One TF-IDF implementation for the core: `tokens`, `tfidf` and `cosine` (which `hygiene.py`, `intent.py` and `groom.py`
read through hygiene), and a frozen comparator set built on them:

  freeze(examples, out)   writes a comparator set: one JSON object per line, the first `{"idf": {...}, "max_df": x}`
                          (the vocabulary and its IDF, fitted once on the examples and frozen), then one
                          `{"label", "text"}` per example; returns the file's sha256. Fitted only at that named event
                          (plan #642 A3: a set that grows would change tomorrow's scores), so the same input always
                          scores the same against the same digest.
  load(path)              the set, `{"idf", "max_df", "examples", "sha256"}`.
  score(set, text)        (top label, its cosine, (runner-up label, its cosine)): each label's score is its nearest
                          example's cosine to `text` under the frozen IDF; a token outside the vocabulary weighs 0.
  label(set, text, threshold, margin)
                          the top label, or ABSTAIN when its cosine is below `threshold` or within `margin` of the
                          runner-up's (A6: a near-tie is as uncertain as a miss, so it returns to inference).
  agreement(set, held_out)
                          over held-out (label, text) cases: n, reproduced, abstained, and `agreement`, the share of all
                          n the set reproduces (an abstention never counts as agreeing; A4's bar is read against it).
It decides nothing on its own: a record of kind `similarity` names its set, digest, threshold, margin and bar (the
`dmc` guard checks them), and its home calls `label`.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("similar.py: Python 3.12+ required")
import hashlib, json, math, re
from collections import Counter
from pathlib import Path
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

TOKEN = re.compile(r"[a-z][a-z0-9]{2,}")
MAX_DF = 0.20          # a token in more than this share of documents is boilerplate, dropped (hygiene's constant, #565)
ABSTAIN = "abstain"    # `label`'s answer inside the margin or below the threshold: the case returns to inference

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("max-df-in-range", lambda: 0 < MAX_DF < 1),
    ("tokens-are-lowercase-words", lambda: tokens("The DMC guard, v1 x") == ["the", "dmc", "guard"]),
    ("cosine-of-a-document-with-itself-is-one", lambda: (lambda v, n: round(cosine(v, n, "a", "a"), 9) == 1.0)(
        *tfidf({"a": "alpha beta", "b": "gamma delta", "c": "epsilon zeta", "d": "eta theta", "e": "iota kappa",
                "f": "lambda sigma"}))),
    ("abstain-is-no-outcome-name", lambda: ABSTAIN == "abstain"),
]


def tokens(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


def tfidf(docs: dict, max_df: float = MAX_DF) -> tuple[dict, dict]:
    """({key: {token: weight}}, {key: norm}) of `docs` ({key: text}): TF-IDF with every token in more than `max_df` of
    the documents dropped as boilerplate."""
    counts = {k: Counter(tokens(t)) for k, t in docs.items()}
    idf = fit_idf(counts.values(), max_df)
    vec = {k: {t: c * idf[t] for t, c in d.items() if t in idf} for k, d in counts.items()}
    return vec, {k: _norm(w) for k, w in vec.items()}


def fit_idf(counts, max_df: float = MAX_DF) -> dict[str, float]:
    """{token: idf} over an iterable of token Counters, a token in more than `max_df` of them dropped."""
    counts = list(counts)
    n = max(len(counts), 1)
    df = Counter(t for d in counts for t in d)
    return {t: math.log(n / c) for t, c in df.items() if c / n <= max_df}


def cosine(vec: dict, norm: dict, a, b) -> float:
    return (sum(v * vec[b].get(t, 0.0) for t, v in vec[a].items()) / (norm[a] * norm[b])) if norm[a] and norm[b] else 0.0


def _norm(w: dict) -> float:
    return math.sqrt(sum(v * v for v in w.values()))


def _vector(idf: dict, text: str) -> dict[str, float]:
    return {t: c * idf[t] for t, c in Counter(tokens(text)).items() if t in idf}


def _cos(a: dict, b: dict) -> float:
    na, nb = _norm(a), _norm(b)
    return sum(v * b.get(t, 0.0) for t, v in a.items()) / (na * nb) if na and nb else 0.0


def freeze(examples: list[tuple[str, str]], out: Path, max_df: float = MAX_DF) -> str:
    """Write the comparator set of `examples` ((label, text) pairs, kept in their order) to `out`; return its sha256.
    The bytes are deterministic: keys sorted, IDF rounded to 12 places, one example per line."""
    if not examples:
        raise ValueError("freeze: no examples")
    idf = fit_idf((Counter(tokens(t)) for _, t in examples), max_df)
    lines = [json.dumps({"idf": {t: round(v, 12) for t, v in sorted(idf.items())}, "max_df": max_df}, sort_keys=True)]
    lines += [json.dumps({"label": lab, "text": text}, sort_keys=True) for lab, text in examples]
    data = ("\n".join(lines) + "\n").encode()
    Path(out).write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def load(path: Path) -> dict:
    """The set at `path`: {idf, max_df, examples: [(label, text)], sha256}. ValueError on a file of another shape."""
    data = Path(path).read_bytes()
    rows = [json.loads(l) for l in data.decode().splitlines() if l.strip()]
    if not rows or "idf" not in rows[0] or any(set(r) != {"label", "text"} for r in rows[1:]) or len(rows) < 2:
        raise ValueError(f"{path}: not a comparator set (a header line, then label/text lines)")
    return {"idf": rows[0]["idf"], "max_df": rows[0].get("max_df", MAX_DF),
            "examples": [(r["label"], r["text"]) for r in rows[1:]], "sha256": hashlib.sha256(data).hexdigest()}


def labels(cset: dict) -> set[str]:
    return {lab for lab, _ in cset["examples"]}


def score(cset: dict, text: str) -> tuple[str, float, tuple[str | None, float]]:
    """(top label, its cosine, (runner-up label or None, its cosine)), each label scored by its nearest example."""
    q = _vector(cset["idf"], text)
    best: dict[str, float] = {}
    for lab, ex in cset["examples"]:
        best[lab] = max(best.get(lab, 0.0), _cos(q, _vector(cset["idf"], ex)))
    ranked = sorted(best.items(), key=lambda kv: (-kv[1], kv[0]))
    top, rest = ranked[0], ranked[1:]
    return top[0], top[1], (rest[0] if rest else (None, 0.0))


def label(cset: dict, text: str, threshold: float, margin: float) -> str:
    """The top label, or ABSTAIN below `threshold` or within `margin` of the runner-up."""
    top, cos, (_, second) = score(cset, text)
    return ABSTAIN if cos < threshold or cos - second < margin else top


def agreement(cset: dict, held_out: list[tuple[str, str]], threshold: float = 0.0, margin: float = 0.0) -> dict:
    """{n, reproduced, abstained, agreement}: `agreement` is reproduced / n (0.0 for no case)."""
    got = [label(cset, text, threshold, margin) for _, text in held_out]
    n = len(held_out)
    reproduced = sum(1 for (want, _), g in zip(held_out, got) if g == want)
    return {"n": n, "reproduced": reproduced, "abstained": sum(1 for g in got if g == ABSTAIN),
            "agreement": reproduced / n if n else 0.0}


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(__doc__)
