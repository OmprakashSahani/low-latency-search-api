from .state import LEX_INDEX


def lexical_topk(query: str, k: int) -> list[tuple[str, float]]:
    return LEX_INDEX.score_query(query, k=k)
