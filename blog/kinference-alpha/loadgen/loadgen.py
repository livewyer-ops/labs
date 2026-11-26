"""Closed-loop load generator for OpenAI-compatible chat endpoints.

Runs N concurrent clients for a fixed duration. Each request streams, so
time to first token (TTFT) and end-to-end latency are measured from the
client side. Prints one JSON line per request, then a summary line.

Workloads:
  shared-prefix  every prompt starts with one of P long shared prefixes
                 (an agent's system prompt and tools), plus a short unique tail
  unique         every prompt is a different long document, read once

Standard library only, so it runs from a plain python image.
"""

import argparse
import http.client
import json
import random
import statistics
import string
import sys
import threading
import time
import urllib.parse


def words(rng, n):
    return " ".join(
        "".join(rng.choice(string.ascii_lowercase) for _ in range(rng.randint(3, 8)))
        for _ in range(n)
    )


def make_prompt(rng, workload, prefixes):
    tail = words(rng, 40)
    if workload == "shared-prefix":
        return rng.choice(prefixes) + "\n\nTask: " + tail
    return words(rng, PROMPT_WORDS) + "\n\nTask: " + tail


def one_request(url, headers, model, prompt, max_tokens):
    u = urllib.parse.urlparse(url)
    conn = http.client.HTTPConnection(u.hostname, u.port or 80, timeout=300)
    body = json.dumps({
        "model": model, "max_tokens": max_tokens, "stream": True,
        "stream_options": {"include_usage": True},
        "messages": [{"role": "user", "content": prompt}],
    })
    start = time.monotonic()
    ttft = None
    try:
        conn.request("POST", "/v1/chat/completions", body,
                     {"content-type": "application/json", **headers})
        resp = conn.getresponse()
        if resp.status != 200:
            resp.read()
            return {"status": resp.status, "ttft": None, "e2e": time.monotonic() - start}
        for raw in resp:
            line = raw.strip()
            if not line.startswith(b"data:") or line == b"data: [DONE]":
                continue
            chunk = json.loads(line[5:])
            if ttft is None and chunk.get("choices") and chunk["choices"][0].get("delta", {}).get("content"):
                ttft = time.monotonic() - start
        return {"status": 200, "ttft": ttft, "e2e": time.monotonic() - start}
    except Exception as e:  # a dropped connection is a result, not a crash
        return {"status": 0, "error": type(e).__name__, "ttft": None, "e2e": time.monotonic() - start}
    finally:
        conn.close()


def pct(xs, p):
    if not xs:
        return None
    xs = sorted(xs)
    return round(xs[min(len(xs) - 1, int(p / 100 * len(xs)))], 3)


def main():
    global PROMPT_WORDS
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--workload", choices=["shared-prefix", "unique"], required=True)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--duration", type=int, default=180)
    ap.add_argument("--warmup", type=int, default=30)
    ap.add_argument("--prefixes", type=int, default=8)
    ap.add_argument("--prompt-words", type=int, default=3000)
    ap.add_argument("--max-tokens", type=int, default=128)
    ap.add_argument("--tenant", default="loadgen")
    ap.add_argument("--model", default="chat")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    PROMPT_WORDS = a.prompt_words

    rng = random.Random(a.seed)
    prefixes = [words(rng, a.prompt_words) for _ in range(a.prefixes)]
    headers = {"x-tenant": a.tenant}
    results, lock = [], threading.Lock()
    t0 = time.monotonic()
    stop_at = t0 + a.warmup + a.duration

    def client(i):
        crng = random.Random(a.seed * 1000 + i)
        while time.monotonic() < stop_at:
            sent = time.monotonic()
            r = one_request(a.url, headers, a.model, make_prompt(crng, a.workload, prefixes), a.max_tokens)
            r.update(label=a.label, t=round(sent - t0, 3), measured=sent - t0 >= a.warmup)
            with lock:  # one writer at a time, so lines from parallel clients never merge
                results.append(r)
                sys.stdout.write(json.dumps(r) + "\n")
                sys.stdout.flush()

    threads = [threading.Thread(target=client, args=(i,)) for i in range(a.concurrency)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    m = [r for r in results if r["measured"]]
    ok = [r for r in m if r["status"] == 200 and r["ttft"] is not None]
    print(json.dumps({
        "summary": a.label, "workload": a.workload, "concurrency": a.concurrency,
        "requests": len(m), "ok": len(ok), "errors": len(m) - len(ok),
        "req_per_min": round(len(ok) / a.duration * 60, 1),
        "ttft_p50": pct([r["ttft"] for r in ok], 50), "ttft_p90": pct([r["ttft"] for r in ok], 90),
        "ttft_p95": pct([r["ttft"] for r in ok], 95),
        "e2e_p50": pct([r["e2e"] for r in ok], 50),
        "ttft_mean": round(statistics.mean(r["ttft"] for r in ok), 3) if ok else None,
    }), flush=True)


if __name__ == "__main__":
    main()
