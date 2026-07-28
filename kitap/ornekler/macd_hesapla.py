#!/usr/bin/env python3
"""Basit MACD hesaplayıcı — eğitim örneği."""

from __future__ import annotations

import csv
from pathlib import Path


def ema(values: list[float], period: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    if len(values) < period:
        return out
    alpha = 2 / (period + 1)
    out[period - 1] = sum(values[:period]) / period
    for i in range(period, len(values)):
        prev = out[i - 1]
        assert prev is not None
        out[i] = alpha * values[i] + (1 - alpha) * prev
    return out


def compute_macd(closes: list[float], fast=12, slow=26, signal=9):
    ema_fast = ema(closes, fast)
    ema_slow = ema(closes, slow)
    macd_line: list[float | None] = [None] * len(closes)
    for i in range(len(closes)):
        if ema_fast[i] is not None and ema_slow[i] is not None:
            macd_line[i] = ema_fast[i] - ema_slow[i]  # type: ignore

    # sinyal: sadece geçerli MACD değerleri üzerinde EMA
    valid_idx = [i for i, v in enumerate(macd_line) if v is not None]
    valid_vals = [macd_line[i] for i in valid_idx]  # type: ignore
    sig_on_valid = ema(valid_vals, signal)  # type: ignore
    signal_line: list[float | None] = [None] * len(closes)
    for i, idx in enumerate(valid_idx):
        signal_line[idx] = sig_on_valid[i]

    hist: list[float | None] = [None] * len(closes)
    for i in range(len(closes)):
        if macd_line[i] is not None and signal_line[i] is not None:
            hist[i] = macd_line[i] - signal_line[i]  # type: ignore
    return macd_line, signal_line, hist


def main():
    sample = Path(__file__).with_name("ornek_fiyatlar.csv")
    closes: list[float] = []
    with sample.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            closes.append(float(row["close"]))

    macd_line, signal_line, hist = compute_macd(closes)
    print(f"{'Bar':>4} {'Close':>8} {'MACD':>10} {'Signal':>10} {'Hist':>10}")
    for i, c in enumerate(closes):
        m = macd_line[i]
        s = signal_line[i]
        h = hist[i]
        if m is None or s is None or h is None:
            continue
        print(f"{i+1:4d} {c:8.2f} {m:10.4f} {s:10.4f} {h:10.4f}")


if __name__ == "__main__":
    main()
