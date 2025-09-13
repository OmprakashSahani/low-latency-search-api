import time
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def stage_timer(stages: dict[str, float], name: str) -> Iterator[None]:
    t0 = time.perf_counter()
    try:
        yield
    finally:
        stages[name] = (time.perf_counter() - t0) * 1000.0  # ms
