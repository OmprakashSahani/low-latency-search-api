import argparse, asyncio, json, math, time
from statistics import mean
import httpx

def percentiles(values, ps=(50,90,99)):
    if not values: return {p: float("nan") for p in ps}
    xs = sorted(values)
    out = {}
    for p in ps:
        if len(xs) == 1:
            out[p] = xs[0]
        else:
            k = (len(xs)-1) * (p/100)
            f = math.floor(k); c = math.ceil(k)
            if f == c:
                out[p] = xs[int(k)]
            else:
                d0 = xs[f]*(c-k)
                d1 = xs[c]*(k-f)
                out[p] = d0 + d1
    return out

async def worker(client, url, payload, latencies, stop_event):
    while not stop_event.is_set():
        t0 = time.perf_counter()
        try:
            r = await client.post(url, json=payload)
            _ = r.status_code  # force fetch
        except Exception:
            # record as large latency to reflect failure impact
            latencies.append(1e9)
        else:
            latencies.append((time.perf_counter()-t0)*1000.0)
    return

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="http://localhost:8000")
    ap.add_argument("--concurrency", type=int, default=100)
    ap.add_argument("--duration", type=int, default=30, help="seconds")
    ap.add_argument("--query", default="bm25 search")
    ap.add_argument("--k", type=int, default=10)
    args = ap.parse_args()

    payload = {"query": args.query, "k": args.k, "use_lexical": True}
    latencies = []
    stop_event = asyncio.Event()

    async with httpx.AsyncClient(base_url=args.host, timeout=10.0) as client:
        # warmup one request path
        try:
            await client.post("/v1/warmup")
        except Exception:
            pass

        # start workers
        tasks = [
            asyncio.create_task(worker(client, "/v1/search", payload, latencies, stop_event))
            for _ in range(args.concurrency)
        ]
        t0 = time.perf_counter()
        await asyncio.sleep(args.duration)
        stop_event.set()
        await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.perf_counter() - t0

    # metrics
    count = len(latencies)
    ok = sum(1 for v in latencies if v < 1e9)
    rps = count/elapsed if elapsed>0 else float("nan")
    p = percentiles([v for v in latencies if v < 1e9])

    print(f"=== Benchmark ===")
    print(f"duration_s      : {elapsed:.2f}")
    print(f"concurrency     : {args.concurrency}")
    print(f"requests_total  : {count}")
    print(f"requests_ok     : {ok}")
    print(f"RPS             : {rps:.2f}")
    print(f"latency_ms p50  : {p.get(50, float('nan')):.3f}")
    print(f"latency_ms p90  : {p.get(90, float('nan')):.3f}")
    print(f"latency_ms p99  : {p.get(99, float('nan')):.3f}")

if __name__ == "__main__":
    asyncio.run(main())
