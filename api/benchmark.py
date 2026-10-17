"""Benchmark retrieval latency for the RAG pipeline.

Times each retrieval stage separately (query embedding, HNSW search, rerank)
so the numbers show where the time actually goes.

python -m api.benchmark
python -m api.benchmark --runs 30 --delay 6
"""
import argparse
import os
import statistics
import time

import cohere
from cohere.errors import TooManyRequestsError

from .index import SOURCES
from .rag import Documents

QUERIES = [
    "What is the difference between symmetric and asymmetric encryption?",
    "How does AES work?",
    "What is a block cipher mode of operation?",
    "Why is ECB mode insecure?",
    "What is a stream cipher?",
    "How does RSA key generation work?",
    "What is Diffie-Hellman key exchange?",
    "What is a cryptographic hash function?",
    "What is a message authentication code?",
    "How does HMAC work?",
    "What is a nonce and why must it not be reused?",
    "What is the Enigma machine?",
    "Who invented public key cryptography?",
    "What is the one-time pad?",
    "What is a padding oracle attack?",
    "What is authenticated encryption?",
    "How do digital signatures work?",
    "What is a Caesar cipher?",
    "What is elliptic curve cryptography?",
    "What is a key derivation function?",
]

STAGES = ("embed", "search", "rerank", "total")
RATE_LIMIT_WAIT_SECONDS = 30


def measure_ms(fn):
    """Runs fn and returns (its result, how long it took in milliseconds)."""
    start = time.perf_counter()
    result = fn()
    elapsed_ms = (time.perf_counter() - start) * 1000
    return result, elapsed_ms


def measure_ms_with_retry(fn):
    """Like measure_ms, but waits and retries on rate limits. Only the successful attempt is timed."""
    while True:
        try:
            return measure_ms(fn)
        except TooManyRequestsError:
            print(f"  rate limited, waiting {RATE_LIMIT_WAIT_SECONDS}s...")
            time.sleep(RATE_LIMIT_WAIT_SECONDS)


def time_one_retrieval(docs: Documents, query: str) -> dict:
    """Runs the same steps as Documents.retrieve and returns each step's time in ms."""
    # 1. Embed the query (Cohere API call, or a cache hit)
    query_emb, embed_ms = measure_ms_with_retry(lambda: docs.embed_query(query))

    # 2. Find the nearest chunks in the local HNSW index
    k = min(docs.retrieve_top_k, len(docs.docs))
    (neighbor_ids, _), search_ms = measure_ms(lambda: docs.idx.knn_query(query_emb, k=k))
    candidates = [docs.docs[i]["text"] for i in neighbor_ids[0]]

    # 3. Rerank those candidates (Cohere API call)
    _, rerank_ms = measure_ms_with_retry(lambda: docs.co.rerank(
        query=query,
        documents=candidates,
        top_n=docs.rerank_top_k,
        model="rerank-english-v3.0",
    ))

    return {
        "embed": embed_ms,
        "search": search_ms,
        "rerank": rerank_ms,
        "total": embed_ms + search_ms + rerank_ms,
    }


def run_pass(docs: Documents, num_queries: int, delay_seconds: float) -> list:
    """Times num_queries retrievals, cycling through QUERIES."""
    samples = []
    for i in range(num_queries):
        query = QUERIES[i % len(QUERIES)]
        try:
            samples.append(time_one_retrieval(docs, query))
        except Exception as e:
            print(f"  skipped ({type(e).__name__}): {query}")
        if delay_seconds:
            time.sleep(delay_seconds)
    return samples


def percentile(values: list, p: float) -> float:
    """Nearest-rank percentile: the value p% of the way through the sorted list."""
    ordered = sorted(values)
    position = round(p / 100 * (len(ordered) - 1))
    return ordered[min(position, len(ordered) - 1)]


def print_report(label: str, samples: list) -> None:
    if not samples:
        print(f"\n{label}: no successful queries.")
        return

    print(f"\nRetrieval latency, {label}, over {len(samples)} queries (ms)")
    print(f"{'stage':<8}{'p50':>9}{'p95':>9}{'mean':>9}{'min':>9}{'max':>9}")
    for stage in STAGES:
        times = [sample[stage] for sample in samples]
        print(f"{stage:<8}"
              f"{percentile(times, 50):>9.2f}"
              f"{percentile(times, 95):>9.2f}"
              f"{statistics.mean(times):>9.2f}"
              f"{min(times):>9.2f}"
              f"{max(times):>9.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs", type=int, default=len(QUERIES), help="number of timed queries per pass")
    parser.add_argument("--delay", type=float, default=0.0,
                        help="seconds between queries (trial keys allow ~10 rerank calls/min, so use ~6)")
    args = parser.parse_args()

    api_key = os.environ.get("COHERE_API_KEY") or os.environ.get("CO_API_KEY")
    if not api_key:
        raise SystemExit("Set COHERE_API_KEY first.")
    client = cohere.ClientV2(api_key)

    docs, ingest_ms = measure_ms(lambda: Documents(SOURCES, client))
    print(f"\nIngestion: {len(docs.docs)} chunks, {len(docs.docs_embs)} embedded, "
          f"in {ingest_ms / 1000:.1f}s (includes rate-limit waits)")

    # Warm-up so connection setup isn't counted against the first query
    time_one_retrieval(docs, "warm-up query")

    # First pass: every query is new, so every embed is a cache miss.
    # Second pass: the same queries again, so every embed is a cache hit.
    cold_samples = run_pass(docs, args.runs, args.delay)
    repeat_samples = run_pass(docs, args.runs, args.delay)

    print_report("cold (cache miss)", cold_samples)
    print_report("repeat (cache hit)", repeat_samples)


if __name__ == "__main__":
    main()
