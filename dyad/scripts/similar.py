#!/usr/bin/env python3
"""Fixed-set similarity over ratified precedents (core script; d-work #642 revision 2; the decision criterion
`dyad/dmc/judgement-complexity.jsonld` names when an agent-side decision is precedent-derivable). Kernel: Python 3.12+,
stdlib only. One TF-IDF implementation for the core: `tokens`, `tfidf` and `cosine` (which `hygiene.py`, `intent.py`
and `groom.py` read through hygiene), and a frozen precedent set built on them:

  freeze(entries, out, ratified, base)
                          writes a precedent set: one JSON object per line, the first `{"idf": {...}, "max_df": x,
                          "base": <commit>}` (the vocabulary and IDF fitted once on the entries, and the `main` commit the
                          set was built at), then one `{"label", "inputs", "fields", "row"}` per ratified case: the outcome
                          it set, its prose inputs, its structured inputs (`fields`, revision 3), and the row whose plan-Y
                          or done-Y covered it.
                          Refused when an entry's row is not in `ratified` (an agent ruling no Y covered is no precedent,
                          Q4; `ratified_rows` reads them from `main`). Returns the file's sha256. Fitted only at that named
                          event and rebuilt when the owner Rule moves or a later Done supersedes a case (Q5), so the same
                          input always scores the same against the same digest.
  load(path)              the set, `{"idf", "max_df", "base", "examples", "rows", "sha256"}`.
  score(set, inputs)      (top label, its cosine, (runner-up label, its cosine)): each label's score is its nearest
                          precedent's cosine to `inputs` under the frozen IDF; a token outside the vocabulary weighs 0.
  label(set, inputs, threshold, margin)
                          the top label, or ABSTAIN when there is no precedent at all (a zero cosine: first of its kind),
                          when its cosine is below `threshold`, or within `margin` of the runner-up's (Q3, Q6: a case
                          that may differ from its precedent stays with the agent, which may depart naming the input).
  decide(set, prose, fields, threshold, margin, read)
                          revision 3: match on the prose inputs, distinguish on the structured fields mechanically, and
                          return {outcome, reason, row, score}: the precedent's outcome, or ABSTAIN with its reason,
                          no-match, near-tie, `distinguish <field>` or prose-only; the precedent row and score cited.
  agreement(set, held_out), loo_agreement(set)
                          over held-out (label, prose, fields) cases, or leave-one-out over the set itself (the re-measure
                          the guard and the sweep run): n, reproduced, abstained, and `agreement`, the share of all n
                          reproduced (an abstention never counts as agreeing; the bar is read against it).
It decides nothing on its own and settles only agent-side calls, never a disposition (Q7): a record of kind `precedent`
names its set, digest, threshold, margin and bar (the `dmc` guard checks them), and its home calls `label`.
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


def ratified_rows(root: Path, at: str = "origin/main") -> set[int]:
    """The ids of the rows on `at` that hold a plan-Y or a done-Y: the rows whose cases may be precedents (Q4)."""
    return {r.id for r in dyadlib.read_rows(root, at=at)
            if re.search(r"\bY (?:plan|done)\b", r.disposed or "")}


def freeze(entries: list[tuple[str, str, dict, int]], out: Path, ratified: set[int], base: str,
           max_df: float = MAX_DF) -> str:
    """Write the precedent set of `entries` ((outcome name, prose inputs, structured fields, covering row), kept in their
    order) to `out`, built at `base`; return its sha256. Refused (ValueError) when an entry's row is not in `ratified`.
    The bytes are deterministic: keys sorted, IDF rounded to 12 places, one precedent per line."""
    if not entries:
        raise ValueError("freeze: no precedents")
    unratified = sorted({row for *_, row in entries if row not in ratified})
    if unratified:
        raise ValueError(f"freeze: row(s) {', '.join(f'#{r}' for r in unratified)} hold no plan-Y or done-Y on main: "
                         f"an agent ruling no Y covered is no precedent (#642 Q4)")
    idf = fit_idf((Counter(tokens(t)) for _, t, _, _ in entries), max_df)
    lines = [json.dumps({"idf": {t: round(v, 12) for t, v in sorted(idf.items())}, "max_df": max_df, "base": base},
                        sort_keys=True)]
    lines += [json.dumps({"label": lab, "inputs": text, "fields": dict(fields), "row": row}, sort_keys=True)
              for lab, text, fields, row in entries]
    data = ("\n".join(lines) + "\n").encode()
    Path(out).write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def load(path: Path) -> dict:
    """The set at `path`: {idf, max_df, base, examples: [(label, inputs)], fields, rows, sha256}. ValueError on another
    shape."""
    data = Path(path).read_bytes()
    rows = [json.loads(l) for l in data.decode().splitlines() if l.strip()]
    if (len(rows) < 2 or "idf" not in rows[0] or "base" not in rows[0]
            or any(set(r) != {"label", "inputs", "fields", "row"} or not isinstance(r["fields"], dict) for r in rows[1:])):
        raise ValueError(f"{path}: not a precedent set (a header line with idf and base, then label/inputs/fields/row lines)")
    return {"idf": rows[0]["idf"], "max_df": rows[0].get("max_df", MAX_DF), "base": rows[0]["base"],
            "examples": [(r["label"], r["inputs"]) for r in rows[1:]], "fields": [r["fields"] for r in rows[1:]],
            "rows": [r["row"] for r in rows[1:]], "sha256": hashlib.sha256(data).hexdigest()}


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
    """The top label, or ABSTAIN with no precedent at all (a zero cosine), below `threshold`, or within `margin` of the
    runner-up."""
    top, cos, (_, second) = score(cset, text)
    return ABSTAIN if cos == 0.0 or cos < threshold or cos - second < margin else top


def decide(cset: dict, prose: str, fields: dict, threshold: float, margin: float,
           read: list[str] = ()) -> dict:
    """#642 revision 3: {outcome, reason, row, score}. Match the case's prose inputs to the nearest precedent; then each
    structured field the precedent holds must equal the case's. The outcome is that precedent's, with reason None, only
    when the match clears `threshold` and `margin` and no field differs; otherwise ABSTAIN with the reason:
    `prose-only` when the case holds a value for an input the record marks `read` (`read`, those values' input names);
    `no-match` below the threshold or with no precedent at all; `near-tie` inside the margin; `distinguish <field>` at
    the first structured field that differs. `row` and `score` cite the matched precedent (R7), on an abstention too."""
    q = _vector(cset["idf"], prose)
    scored = [(_cos(q, _vector(cset["idf"], ex)), i) for i, (_, ex) in enumerate(cset["examples"])]
    best_by_label: dict[str, tuple[float, int]] = {}
    for cos, i in scored:
        lab = cset["examples"][i][0]
        if cos > best_by_label.get(lab, (-1.0, -1))[0]:
            best_by_label[lab] = (cos, i)
    ranked = sorted(best_by_label.items(), key=lambda kv: (-kv[1][0], kv[0]))
    (top, (cos, i)), second = ranked[0], (ranked[1][1][0] if len(ranked) > 1 else 0.0)
    cite = {"row": cset["rows"][i], "score": round(cos, 6)}
    if read:
        return {"outcome": ABSTAIN, "reason": "prose-only", **cite}
    if cos == 0.0 or cos < threshold:
        return {"outcome": ABSTAIN, "reason": "no-match", **cite}
    if cos - second < margin:
        return {"outcome": ABSTAIN, "reason": "near-tie", **cite}
    for field, value in sorted(cset["fields"][i].items()):
        if fields.get(field) != value:
            return {"outcome": ABSTAIN, "reason": f"distinguish {field}", **cite}
    return {"outcome": top, "reason": None, **cite}


def agreement(cset: dict, held_out: list[tuple[str, str, dict]], threshold: float = 0.0, margin: float = 0.0) -> dict:
    """{n, reproduced, abstained, agreement} over held-out (outcome, prose, fields) cases decided by `decide`:
    `agreement` is reproduced / n (0.0 for no case); an abstention never counts as agreeing."""
    got = [decide(cset, prose, fields, threshold, margin)["outcome"] for _, prose, fields in held_out]
    n = len(held_out)
    reproduced = sum(1 for (want, _, _), g in zip(held_out, got) if g == want)
    return {"n": n, "reproduced": reproduced, "abstained": sum(1 for g in got if g == ABSTAIN),
            "agreement": reproduced / n if n else 0.0}


def loo_agreement(cset: dict, threshold: float = 0.0, margin: float = 0.0) -> dict:
    """The set's own re-measure (R3): each precedent decided by the set without it (leave-one-out), its IDF the frozen
    one; `agreement` as `agreement` gives it. A set of one case reproduces nothing."""
    n = len(cset["examples"])
    held = []
    for k in range(n):
        rest = {**cset, "examples": cset["examples"][:k] + cset["examples"][k + 1:],
                "fields": cset["fields"][:k] + cset["fields"][k + 1:], "rows": cset["rows"][:k] + cset["rows"][k + 1:]}
        held.append((cset["examples"][k][0], rest))
    got = [decide(rest, cset["examples"][k][1], cset["fields"][k], threshold, margin)["outcome"] if rest["examples"]
           else ABSTAIN for k, (_, rest) in enumerate(held)]
    reproduced = sum(1 for (want, _), g in zip(held, got) if g == want)
    return {"n": n, "reproduced": reproduced, "abstained": sum(1 for g in got if g == ABSTAIN),
            "agreement": reproduced / n if n else 0.0}


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(__doc__)
