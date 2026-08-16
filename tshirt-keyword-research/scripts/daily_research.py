#!/usr/bin/env python3
"""Daily t-shirt keyword research across Amazon, eBay, Google, and related POD signals.

Collects live autocomplete suggestions (what shoppers actually start typing) and
writes a JSON snapshot plus a Turkish markdown brief.

Usage:
    python3 tshirt-keyword-research/scripts/daily_research.py
    python3 tshirt-keyword-research/scripts/daily_research.py --date 2026-08-16
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
CTX = ssl.create_default_context()

SEEDS = [
    "t shirt",
    "tshirt",
    "graphic tee",
    "funny t shirt",
    "halloween shirt",
    "teacher shirt",
    "nurse shirt",
    "dog mom shirt",
    "cat mom shirt",
    "vintage t shirt",
    "world cup shirt",
    "soccer shirt",
    "pumpkin spice shirt",
    "fall shirt",
    "oversized t shirt",
    "back to school shirt",
    "football shirt",
    "comfort colors",
    "band t shirt",
    "book lover shirt",
    "gamer shirt",
    "christian shirt",
    "matching family shirt",
    "labor day shirt",
    "boo crew shirt",
    "football mom shirt",
    "first day of school shirt",
    "kindergarten shirt",
    "y2k graphic tee",
    "anime t shirt",
    "f1 shirt",
    "formula 1 shirt",
    "halloween teacher shirt",
    "cottagecore shirt",
    "coquette shirt",
    "bookish shirt",
]


def http_get(url: str, timeout: int = 20) -> tuple[int | None, bytes]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"},
    )
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as resp:
            return resp.status, resp.read()[:120_000]
    except Exception as exc:  # noqa: BLE001 — network errors are expected
        return None, str(exc).encode("utf-8", "replace")


def amazon_suggest(seed: str, marketplace: str = "ATVPDKIKX0DER") -> list[str]:
    q = urllib.parse.quote(seed)
    url = (
        "https://completion.amazon.com/api/2017/suggestions"
        f"?mid={marketplace}&alias=aps&prefix={q}&limit=11"
    )
    status, body = http_get(url)
    if status != 200:
        return []
    try:
        payload = json.loads(body.decode("utf-8", "replace"))
    except json.JSONDecodeError:
        return []
    return [item.get("value") for item in payload.get("suggestions", []) if item.get("value")]


def ebay_suggest(seed: str) -> list[str]:
    q = urllib.parse.quote(seed)
    url = f"https://www.ebay.com/autosug?kwd={q}&sId=0&_sop=12"
    status, body = http_get(url)
    if status != 200:
        return []
    text = body.decode("utf-8", "replace")
    match = re.search(r'"sug"\s*:\s*(\[[^\]]*\])', text)
    if not match:
        return []
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return []


def google_suggest(seed: str) -> list[str]:
    q = urllib.parse.quote(seed)
    url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={q}"
    status, body = http_get(url)
    if status != 200:
        return []
    try:
        payload = json.loads(body.decode("utf-8", "replace"))
    except json.JSONDecodeError:
        return []
    if isinstance(payload, list) and len(payload) > 1 and isinstance(payload[1], list):
        return [str(item) for item in payload[1]]
    return []


def collect() -> dict:
    amazon: dict[str, list[str]] = {}
    ebay: dict[str, list[str]] = {}
    google: dict[str, list[str]] = {}
    errors: list[str] = []

    for seed in SEEDS:
        try:
            amazon[seed] = amazon_suggest(seed)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"amazon:{seed}:{exc}")
            amazon[seed] = []
        try:
            ebay[seed] = ebay_suggest(seed)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"ebay:{seed}:{exc}")
            ebay[seed] = []
        try:
            google[seed] = google_suggest(seed)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"google:{seed}:{exc}")
            google[seed] = []

    return {
        "amazon": amazon,
        "ebay": ebay,
        "google": google,
        "errors": errors,
    }


def flatten(source: dict[str, list[str]]) -> list[str]:
    values: list[str] = []
    for items in source.values():
        values.extend(items)
    return values


def top_phrases(values: list[str], limit: int = 25) -> list[tuple[str, int]]:
    counter = Counter(v.strip().lower() for v in values if v and v.strip())
    return counter.most_common(limit)


def render_report(date: str, snapshot: dict) -> str:
    amazon_top = top_phrases(flatten(snapshot["amazon"]))
    ebay_top = top_phrases(flatten(snapshot["ebay"]))
    google_top = top_phrases(flatten(snapshot["google"]))

    def bullets(pairs: list[tuple[str, int]]) -> str:
        if not pairs:
            return "- Veri alınamadı (platform isteği engellenmiş olabilir)."
        return "\n".join(f"- `{phrase}` ({count})" for phrase, count in pairs)

    def seed_block(source: dict[str, list[str]], seeds: list[str]) -> str:
        lines = []
        for seed in seeds:
            items = source.get(seed) or []
            if not items:
                continue
            joined = ", ".join(f"`{item}`" for item in items[:8])
            lines.append(f"- **{seed}:** {joined}")
        return "\n".join(lines) if lines else "- Bu çekimde öneri dönmedi."

    highlight_seeds = [
        "halloween shirt",
        "teacher shirt",
        "fall shirt",
        "pumpkin spice shirt",
        "graphic tee",
        "vintage t shirt",
        "world cup shirt",
        "football mom shirt",
        "dog mom shirt",
        "f1 shirt",
        "back to school shirt",
        "y2k graphic tee",
    ]

    return f"""# T-shirt anahtar kelime raporu — {date}

Otomatik çekim. Amazon, eBay ve Google otomatik tamamlama (autocomplete) verisi.
Redbubble / TeePublic / Pinterest sayfaları bot koruması nedeniyle bu scriptte
doğrudan çekilemez; o platformlar için günlük rapordaki manuel/kaynak özetine bakın.

## Amazon — en sık önerilen ifadeler

{bullets(amazon_top)}

## eBay — en sık önerilen ifadeler

{bullets(ebay_top)}

## Google — en sık önerilen ifadeler

{bullets(google_top)}

## Amazon tohum kelime detayı

{seed_block(snapshot["amazon"], highlight_seeds)}

## eBay tohum kelime detayı

{seed_block(snapshot["ebay"], highlight_seeds)}

## Kaynak notu

- Amazon Completion API (`completion.amazon.com`, US marketplace)
- eBay Autosuggest (`ebay.com/autosug`)
- Google Suggest (`suggestqueries.google.com`)
- Çekim zamanı (UTC): {snapshot.get("collected_at_utc", "bilinmiyor")}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Daily t-shirt keyword research")
    parser.add_argument("--date", default=datetime.now(timezone.utc).date().isoformat())
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Collecting autocomplete for {args.date}...", file=sys.stderr)
    sources = collect()
    snapshot = {
        "date": args.date,
        "collected_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "seeds": SEEDS,
        **sources,
    }

    json_path = DATA_DIR / f"{args.date}.json"
    json_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    auto_report = REPORTS_DIR / f"{args.date}-autocomplete.md"
    auto_report.write_text(render_report(args.date, snapshot), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {auto_report}")
    amazon_count = sum(len(v) for v in sources["amazon"].values())
    ebay_count = sum(len(v) for v in sources["ebay"].values())
    google_count = sum(len(v) for v in sources["google"].values())
    print(f"Amazon phrases: {amazon_count} | eBay: {ebay_count} | Google: {google_count}")
    if sources["errors"]:
        print("Errors:", *sources["errors"], sep="\n- ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
