#!/usr/bin/env python3
"""Daily POD product-signal collector for Redbubble, TeePublic, and Etsy.

Collects live Google Suggest phrases for marketplace + product + niche seeds.
Redbubble / TeePublic / Etsy storefronts are bot-protected, so this script
captures what shoppers type, not live listing HTML.

Usage:
    python3 pod-research/scripts/daily_research.py
    python3 pod-research/scripts/daily_research.py --date 2026-08-20
"""

from __future__ import annotations

import argparse
import json
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
    # marketplace + product
    "redbubble sticker",
    "redbubble tshirt",
    "redbubble hoodie",
    "redbubble poster",
    "etsy tshirt",
    "etsy sticker",
    "etsy sweatshirt",
    "etsy halloween shirt",
    "etsy halloween sticker",
    "teepublic tshirt",
    "teepublic sticker",
    "print on demand halloween",
    # +40 day US window: week of Sept 29 = Halloween buying peak
    "halloween shirts for women",
    "halloween sweatshirt",
    "spooky season sweatshirt",
    "vintage halloween shirt",
    "retro halloween sweatshirt",
    "pink halloween sweatshirt",
    "coquette halloween shirt",
    "witchcore sweatshirt",
    "teacher halloween shirt",
    "cat mom halloween shirt",
    "bookish halloween shirt",
    "cute ghost reading shirt",
    "pumpkin spice shirt",
    "halloween sticker pack",
    "papercraft sticker",
    "paper cut halloween",
    "gothic cottagecore halloween",
    "black cat halloween sticker",
    "pet halloween bandana",
    "dog halloween shirt",
    "matching family halloween shirts",
    "halloween party shirt",
    "comfort colors halloween",
    "fall teacher shirt",
    "breast cancer awareness shirt",
    "hispanic heritage month shirt",
    "october halloween decor",
]


def http_get(url: str, timeout: int = 20) -> tuple[int | None, bytes]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"},
    )
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as resp:
            return resp.status, resp.read()[:120_000]
    except Exception as exc:  # noqa: BLE001
        return None, str(exc).encode("utf-8", "replace")


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
    google: dict[str, list[str]] = {}
    errors: list[str] = []
    for seed in SEEDS:
        try:
            google[seed] = google_suggest(seed)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"google:{seed}:{exc}")
            google[seed] = []
    return {"google": google, "errors": errors}


def flatten(source: dict[str, list[str]]) -> list[str]:
    values: list[str] = []
    for items in source.values():
        values.extend(items)
    return values


def top_phrases(values: list[str], limit: int = 30) -> list[tuple[str, int]]:
    counter = Counter(v.strip().lower() for v in values if v and v.strip())
    return counter.most_common(limit)


def render_auto_report(date: str, snapshot: dict) -> str:
    google_top = top_phrases(flatten(snapshot["google"]))

    def bullets(pairs: list[tuple[str, int]]) -> str:
        if not pairs:
            return "- Veri alınamadı (istek engellenmiş olabilir)."
        return "\n".join(f"- `{phrase}` ({count})" for phrase, count in pairs)

    lines = [
        f"# POD arama sinyali — {date}",
        "",
        "Otomatik Google Suggest çekimi. Redbubble / TeePublic / Etsy vitrin HTML",
        "bot koruması nedeniyle bu scriptte çekilmez; günlük brifingde yayınlanmış",
        "trend raporları ile birleştirilir.",
        "",
        "## En sık önerilen ifadeler",
        "",
        bullets(google_top),
        "",
        "## Tohum kelime detayı",
        "",
    ]
    for seed in SEEDS:
        items = snapshot["google"].get(seed) or []
        if not items:
            continue
        joined = ", ".join(f"`{item}`" for item in items[:8])
        lines.append(f"- **{seed}:** {joined}")
    lines.extend(
        [
            "",
            "## Kaynak notu",
            "",
            "- Google Suggest (`suggestqueries.google.com`)",
            f"- Çekim zamanı (UTC): {snapshot.get('collected_at_utc', 'bilinmiyor')}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Daily POD marketplace research")
    parser.add_argument("--date", default=datetime.now(timezone.utc).date().isoformat())
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Collecting Google Suggest for {args.date}...", file=sys.stderr)
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
    auto_report.write_text(render_auto_report(args.date, snapshot), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {auto_report}")
    google_count = sum(len(v) for v in sources["google"].values())
    print(f"Google phrases: {google_count}")
    if sources["errors"]:
        print("Errors:", *sources["errors"], sep="\n- ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
