import math
from dataclasses import dataclass
from typing import Any

from ..utils.tokenization import tokenize


# ---- Doc store & postings -----------------------------------------------------
@dataclass(slots=True)
class Doc:
    id: str
    text: str
    meta: dict[str, Any]


class LexicalIndex:
    """
    Minimal in-memory BM25 index.
    - postings: term -> {doc_id: tf}
    - doclen: doc_id -> length (in tokens)
    - N, avgdl maintained incrementally with cached _avgdl
    """

    def __init__(self, k1: float = 1.2, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.docs: dict[str, Doc] = {}
        self.postings: dict[str, dict[str, int]] = {}
        self.doclen: dict[str, int] = {}
        self.N = 0
        self._tok_cache: dict[str, list[str]] = {}
        self._avgdl: float = 0.0  # cached average doc length

    # ---- internal helpers ----
    def _recompute_avgdl(self) -> None:
        self._avgdl = (sum(self.doclen.values()) / self.N) if self.N else 0.0

    # ---- write path ----
    def add(self, doc_id: str, text: str, meta: dict[str, Any] | None = None) -> None:
        meta = meta or {}
        if doc_id in self.docs:
            # naive update: remove then add
            self.remove(doc_id)

        toks = tokenize(text)
        self._tok_cache[doc_id] = toks
        self.docs[doc_id] = Doc(id=doc_id, text=text, meta=meta)
        self.doclen[doc_id] = len(toks)
        self.N += 1

        tf: dict[str, int] = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        for term, f in tf.items():
            bucket = self.postings.setdefault(term, {})
            bucket[doc_id] = f

        self._recompute_avgdl()

    def remove(self, doc_id: str) -> None:
        if doc_id not in self.docs:
            return

        toks = self._tok_cache.pop(doc_id, [])
        # recompute term frequencies for this doc on the fly
        tf: dict[str, int] = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1

        for term in tf:  # no .keys(); faster membership iteration
            bucket = self.postings.get(term)
            if bucket and doc_id in bucket:
                del bucket[doc_id]
                if not bucket:
                    del self.postings[term]

        del self.docs[doc_id]
        _ = self.doclen.pop(doc_id, None)
        self.N = max(0, self.N - 1)
        self._recompute_avgdl()

    # ---- read path ----
    @property
    def avgdl(self) -> float:
        return self._avgdl

    def bm25_idf(self, term: str) -> float:
        # Standard BM25 IDF (with +0.5 smoothing)
        df = len(self.postings.get(term, {}))
        if df == 0 or self.N == 0:
            return 0.0
        return math.log((self.N - df + 0.5) / (df + 0.5) + 1e-9)

    def score_query(self, query: str, k: int = 10) -> list[tuple[str, float]]:
        if self.N == 0:
            return []
        q_terms = tokenize(query)
        if not q_terms:
            return []

        # candidate docs = union of postings for query terms
        candidates: dict[str, float] = {}
        avgdl = self._avgdl or 1.0  # guard against divide-by-zero
        for term in q_terms:
            plist = self.postings.get(term)
            if not plist:
                continue
            idf = self.bm25_idf(term)
            if idf == 0.0:
                continue
            for doc_id, tf in plist.items():
                dl = self.doclen[doc_id]
                denom = tf + self.k1 * (1.0 - self.b + self.b * (dl / avgdl))
                score_add = idf * (tf * (self.k1 + 1.0)) / (denom or 1.0)
                candidates[doc_id] = candidates.get(doc_id, 0.0) + score_add

        # top-k
        items = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
        return items[: max(1, k)]

    def snippet(self, doc_id: str, query: str, window: int = 24) -> str:
        # cheap snippet around first occurrence (token-level window)
        text = self.docs[doc_id].text
        toks = self._tok_cache.get(doc_id) or tokenize(text)
        q = tokenize(query)
        if not toks or not q:
            return text[:160]
        qset = set(q)
        first = None
        for i, t in enumerate(toks):
            if t in qset:
                first = i
                break
        if first is None:
            return text[:160]
        lo = max(0, first - window // 2)
        hi = min(len(toks), lo + window)
        frag = " ".join(toks[lo:hi])
        return frag[:200]
