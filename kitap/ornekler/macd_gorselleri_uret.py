#!/usr/bin/env python3
"""MACD kitabı için örnek grafikler üretir."""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

OUT = Path(__file__).resolve().parents[1] / "gorseller"
OUT.mkdir(parents=True, exist_ok=True)

# Türkçe uyumlu basit stil
plt.rcParams.update({
    "figure.facecolor": "#0f1419",
    "axes.facecolor": "#151b23",
    "axes.edgecolor": "#3d4a5c",
    "axes.labelcolor": "#d7dee8",
    "xtick.color": "#9aa7b8",
    "ytick.color": "#9aa7b8",
    "text.color": "#e8eef6",
    "grid.color": "#243041",
    "grid.alpha": 0.7,
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "legend.facecolor": "#1a2330",
    "legend.edgecolor": "#3d4a5c",
    "savefig.dpi": 160,
    "savefig.bbox": "tight",
})


def ema(series: np.ndarray, period: int) -> np.ndarray:
    out = np.full_like(series, np.nan, dtype=float)
    if len(series) < period:
        return out
    alpha = 2 / (period + 1)
    out[period - 1] = series[:period].mean()
    for i in range(period, len(series)):
        out[i] = alpha * series[i] + (1 - alpha) * out[i - 1]
    return out


def macd(close: np.ndarray, fast=12, slow=26, signal=9):
    ema_fast = ema(close, fast)
    ema_slow = ema(close, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(np.nan_to_num(macd_line, nan=0.0), signal)
    # sinyal EMA'sını MACD geçerli olduktan sonra hesapla
    valid = ~np.isnan(macd_line)
    signal_line = np.full_like(macd_line, np.nan)
    macd_valid = macd_line[valid]
    if len(macd_valid) >= signal:
        sig = ema(macd_valid, signal)
        signal_line[np.where(valid)[0]] = sig
    hist = macd_line - signal_line
    return ema_fast, ema_slow, macd_line, signal_line, hist


def style_ax(ax, title=None):
    ax.grid(True, linestyle="--", linewidth=0.6)
    if title:
        ax.set_title(title, pad=10, color="#f2f6fb")
    for spine in ax.spines.values():
        spine.set_color("#3d4a5c")


def plot_price_macd(close, title, filename, annotate=None, highlight=None):
    n = len(close)
    x = np.arange(n)
    ema_f, ema_s, m, s, h = macd(close)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11, 7), sharex=True,
        gridspec_kw={"height_ratios": [2.1, 1.2], "hspace": 0.08},
    )

    ax1.plot(x, close, color="#5eb1ff", lw=1.8, label="Fiyat (kapanış)")
    ax1.plot(x, ema_f, color="#ffb347", lw=1.2, alpha=0.9, label="EMA 12")
    ax1.plot(x, ema_s, color="#c084fc", lw=1.2, alpha=0.9, label="EMA 26")
    style_ax(ax1, title)
    ax1.legend(loc="upper left", fontsize=8)

    colors = np.where(h >= 0, "#22c55e", "#ef4444")
    ax2.bar(x, h, color=colors, width=0.8, alpha=0.75, label="Histogram")
    ax2.plot(x, m, color="#38bdf8", lw=1.6, label="MACD çizgisi")
    ax2.plot(x, s, color="#f472b6", lw=1.4, label="Sinyal çizgisi")
    ax2.axhline(0, color="#94a3b8", lw=0.9, ls="--")
    style_ax(ax2)
    ax2.legend(loc="upper left", fontsize=8, ncol=3)
    ax2.set_xlabel("Bar (zaman)")

    if highlight:
        for a, b, color, alpha in highlight:
            for ax in (ax1, ax2):
                ax.axvspan(a, b, color=color, alpha=alpha)

    if annotate:
        for ax_name, args in annotate:
            ax = ax1 if ax_name == "price" else ax2
            ax.annotate(**args)

    fig.savefig(OUT / filename)
    plt.close(fig)
    print("wrote", filename)


def make_trending_up(n=120, seed=7):
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 8, n)
    noise = rng.normal(0, 0.6, n).cumsum() * 0.15
    return 100 + t * 3.2 + np.sin(t * 1.3) * 2.5 + noise


def make_trending_down(n=120, seed=11):
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 8, n)
    noise = rng.normal(0, 0.55, n).cumsum() * 0.12
    return 140 - t * 3.0 + np.sin(t * 1.1) * 2.2 + noise


def make_range(n=120, seed=3):
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 10, n)
    return 100 + np.sin(t * 1.8) * 4 + rng.normal(0, 0.5, n).cumsum() * 0.08


def make_bullish_divergence(n=140, seed=21):
    """Fiyat daha düşük dip, MACD daha yüksek dip üretecek senaryo."""
    rng = np.random.default_rng(seed)
    close = np.zeros(n)
    close[0] = 120
    # düşüş, toparlanma, daha derin dip, sonra yükseliş
    for i in range(1, n):
        if i < 35:
            close[i] = close[i - 1] - 0.55 + rng.normal(0, 0.35)
        elif i < 55:
            close[i] = close[i - 1] + 0.7 + rng.normal(0, 0.3)
        elif i < 90:
            # ikinci düşüş daha derin ama momentum zayıf
            close[i] = close[i - 1] - 0.35 + rng.normal(0, 0.25)
        else:
            close[i] = close[i - 1] + 0.85 + rng.normal(0, 0.3)
    # ikinci dibi fiyat olarak netleştir
    close[85:92] = np.linspace(close[85], min(close[:90]) - 2.5, 7)
    close[92:] = close[91] + np.cumsum(np.abs(rng.normal(0.55, 0.25, n - 92)))
    return close


def make_bearish_divergence(n=140, seed=29):
    rng = np.random.default_rng(seed)
    close = np.zeros(n)
    close[0] = 90
    for i in range(1, n):
        if i < 40:
            close[i] = close[i - 1] + 0.65 + rng.normal(0, 0.3)
        elif i < 60:
            close[i] = close[i - 1] - 0.55 + rng.normal(0, 0.28)
        elif i < 95:
            close[i] = close[i - 1] + 0.45 + rng.normal(0, 0.25)
        else:
            close[i] = close[i - 1] - 0.8 + rng.normal(0, 0.3)
    close[88:96] = np.linspace(close[88], max(close[:95]) + 2.8, 8)
    close[96:] = close[95] - np.cumsum(np.abs(rng.normal(0.5, 0.22, n - 96)))
    return close


def make_whipsaw(n=100, seed=41):
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 14, n)
    return 100 + np.sin(t * 2.4) * 3.5 + rng.normal(0, 0.4, n)


def fig_bilesenler():
    """MACD üç bileşen şeması."""
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("MACD’nin Üç Bileşeni", color="#f2f6fb", pad=14)

    boxes = [
        (0.5, 3.2, 2.8, 2.0, "#1e3a5f", "1) MACD Çizgisi\nEMA12 − EMA26\nMomentumun çekirdeği"),
        (3.6, 3.2, 2.8, 2.0, "#4a1942", "2) Sinyal Çizgisi\nMACD’nin EMA9’u\nTetik / filtre"),
        (6.7, 3.2, 2.8, 2.0, "#1a3d2e", "3) Histogram\nMACD − Sinyal\nMomentum ivmesi"),
    ]
    for x, y, w, h, c, txt in boxes:
        ax.add_patch(mpatches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.2",
            facecolor=c, edgecolor="#8b9bb0", lw=1.5,
        ))
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center",
                fontsize=11, color="#eef3f9")

    ax.add_patch(mpatches.FancyBboxPatch(
        (1.5, 0.5), 7, 1.8, boxstyle="round,pad=0.05,rounding_size=0.2",
        facecolor="#222b38", edgecolor="#64748b", lw=1.2,
    ))
    ax.text(5, 1.4,
            "Standart ayar: (12, 26, 9)\n"
            "Gerald Appel (1977) • Histogram: Thomas Aspray (1986)",
            ha="center", va="center", fontsize=11, color="#cbd5e1")
    fig.savefig(OUT / "01-macd-bilesenler.png")
    plt.close(fig)
    print("wrote 01-macd-bilesenler.png")


def fig_formul_akisi():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_title("MACD Hesaplama Akışı", color="#f2f6fb", pad=12)

    steps = [
        (1, 6.5, "Kapanış fiyatları"),
        (1, 5.0, "EMA(12) ve EMA(26)"),
        (1, 3.5, "MACD = EMA12 − EMA26"),
        (1, 2.0, "Sinyal = EMA(9) of MACD"),
        (1, 0.5, "Histogram = MACD − Sinyal"),
    ]
    for i, (x, y, txt) in enumerate(steps):
        ax.add_patch(mpatches.FancyBboxPatch(
            (x, y), 8, 1.0, boxstyle="round,pad=0.02,rounding_size=0.15",
            facecolor="#1b2838", edgecolor="#38bdf8", lw=1.4,
        ))
        ax.text(5, y + 0.5, f"{i + 1}.  {txt}", ha="center", va="center",
                fontsize=13, color="#e2e8f0")
        if i < len(steps) - 1:
            ax.annotate("", xy=(5, steps[i + 1][1] + 1.0), xytext=(5, y),
                        arrowprops=dict(arrowstyle="->", color="#94a3b8", lw=1.5))
    fig.savefig(OUT / "02-hesaplama-akisi.png")
    plt.close(fig)
    print("wrote 02-hesaplama-akisi.png")


def fig_hesap_ornek_tablo():
    """Küçük sayısal örnek tablosu görseli."""
    closes = np.array([
        100, 101, 102.5, 101.8, 103, 104.2, 103.5, 105, 106.1, 105.4,
        107, 108.2, 107.5, 109, 110.5, 109.8, 111, 112.3, 111.5, 113,
        114.2, 113.6, 115, 116.4, 115.8, 117, 118.5, 117.9, 119.2, 120.5,
        119.8, 121, 122.4, 121.7, 123, 124.2, 123.5, 125, 126.1, 125.4,
    ], dtype=float)
    _, _, m, s, h = macd(closes)
    # son 8 geçerli satır
    idx = np.where(~np.isnan(h))[0][-8:]

    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.axis("off")
    ax.set_title("Sayısal Örnek — Son 8 Bar (12,26,9)", color="#f2f6fb", pad=8)

    cell = [["Bar", "Kapanış", "MACD", "Sinyal", "Histogram"]]
    for i in idx:
        cell.append([
            str(i + 1),
            f"{closes[i]:.2f}",
            f"{m[i]:.3f}",
            f"{s[i]:.3f}",
            f"{h[i]:.3f}",
        ])
    table = ax.table(cellText=cell, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.6)
    for (r, c), cell_obj in table.get_celld().items():
        cell_obj.set_edgecolor("#3d4a5c")
        if r == 0:
            cell_obj.set_facecolor("#1e3a5f")
            cell_obj.get_text().set_color("#e2e8f0")
        else:
            cell_obj.set_facecolor("#151b23" if r % 2 else "#1a2330")
            cell_obj.get_text().set_color("#dbe4ef")
            if c == 4:
                val = float(cell[r][4])
                cell_obj.get_text().set_color("#22c55e" if val >= 0 else "#ef4444")
    fig.savefig(OUT / "03-sayisal-ornek-tablo.png")
    plt.close(fig)
    print("wrote 03-sayisal-ornek-tablo.png")
    # ham veriyi de kaydet
    np.savetxt(OUT.parent / "ornekler" / "ornek_fiyatlar.csv", closes, fmt="%.4f", header="close", comments="")


def main():
    fig_bilesenler()
    fig_formul_akisi()
    fig_hesap_ornek_tablo()

    up = make_trending_up()
    plot_price_macd(
        up,
        "Yükseliş Trendi — MACD Sıfır Üstünde ve Genişleyen Histogram",
        "04-yukselis-trendi.png",
        highlight=[(70, 110, "#22c55e", 0.08)],
    )

    down = make_trending_down()
    plot_price_macd(
        down,
        "Düşüş Trendi — MACD Sıfır Altında",
        "05-dusus-trendi.png",
        highlight=[(65, 110, "#ef4444", 0.08)],
    )

    # çapraz sinyalli senaryo
    rng = np.random.default_rng(9)
    cross = 100 + np.cumsum(rng.normal(0.15, 0.9, 130))
    cross[40:55] += np.linspace(0, 8, 15)
    cross[55:70] -= np.linspace(0, 6, 15)
    cross[70:95] += np.linspace(0, 12, 25)
    plot_price_macd(
        cross,
        "Sinyal Çizgisi Kesişimleri (Al / Sat Tetikleri)",
        "06-sinyal-kesisimleri.png",
    )

    rng = np.random.default_rng(15)
    zero = 95 + np.cumsum(rng.normal(0.05, 0.7, 140))
    zero[50:90] += np.linspace(0, 18, 40)
    zero[90:] -= np.linspace(0, 10, 50)
    plot_price_macd(
        zero,
        "Sıfır Çizgisi Geçişleri — Trend Bias Değişimi",
        "07-sifir-cizgisi.png",
    )

    hist = make_trending_up(n=110, seed=5)
    # ivme kaybı ekle
    hist[75:] = hist[74] + np.cumsum(np.random.default_rng(6).normal(0.05, 0.5, 35))
    plot_price_macd(
        hist,
        "Histogram: Genişleme (ivme artışı) ve Daralma (ivme kaybı)",
        "08-histogram-ivme.png",
        highlight=[(45, 70, "#22c55e", 0.07), (75, 105, "#f59e0b", 0.08)],
    )

    bull_div = make_bullish_divergence()
    plot_price_macd(
        bull_div,
        "Bullish (Yükseliş) Iraksama — Fiyat LL, MACD HL",
        "09-bullish-divergence.png",
        highlight=[(25, 40, "#38bdf8", 0.08), (80, 95, "#38bdf8", 0.08)],
    )

    bear_div = make_bearish_divergence()
    plot_price_macd(
        bear_div,
        "Bearish (Düşüş) Iraksama — Fiyat HH, MACD LH",
        "10-bearish-divergence.png",
        highlight=[(30, 45, "#f472b6", 0.08), (85, 100, "#f472b6", 0.08)],
    )

    whip = make_whipsaw()
    plot_price_macd(
        whip,
        "Yanlış Sinyaller (Whipsaw) — Yatay / Gürültülü Piyasa",
        "11-whipsaw-yanlis-sinyal.png",
    )

    # ayar karşılaştırması
    close = make_trending_up(n=150, seed=2) + make_range(n=150, seed=8) * 0.15
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True,
                             gridspec_kw={"hspace": 0.12})
    settings = [(12, 26, 9, "Standart 12-26-9"), (5, 13, 5, "Hızlı 5-13-5"),
                (19, 39, 9, "Yavaş 19-39-9")]
    x = np.arange(len(close))
    for ax, (f, sl, sg, label) in zip(axes, settings):
        _, _, m, s, h = macd(close, f, sl, sg)
        colors = np.where(np.nan_to_num(h) >= 0, "#22c55e", "#ef4444")
        ax.bar(x, h, color=colors, width=0.8, alpha=0.7)
        ax.plot(x, m, color="#38bdf8", lw=1.4, label="MACD")
        ax.plot(x, s, color="#f472b6", lw=1.2, label="Sinyal")
        ax.axhline(0, color="#94a3b8", lw=0.8, ls="--")
        style_ax(ax, label)
        ax.legend(loc="upper left", fontsize=8)
    axes[-1].set_xlabel("Bar (zaman)")
    fig.suptitle("Aynı Fiyat — Farklı MACD Ayarları", color="#f2f6fb", y=0.98, fontsize=14)
    fig.savefig(OUT / "12-ayar-karsilastirma.png")
    plt.close(fig)
    print("wrote 12-ayar-karsilastirma.png")

    # strateji özet şeması
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("Pratik MACD Karar Akışı", color="#f2f6fb", pad=12)
    items = [
        (0.4, 5.2, 3.4, 1.4, "#14532d", "1. Üst zaman dilimi\ntrendini belirle"),
        (4.3, 5.2, 3.4, 1.4, "#1e3a5f", "2. MACD sinyali\n(kesişim / ıraksama)"),
        (8.2, 5.2, 3.4, 1.4, "#4a1942", "3. Mum / yapı\nonayı bekle"),
        (2.0, 2.8, 3.6, 1.4, "#3b2f0b", "4. Risk: stop & hedef\nbelirle"),
        (6.4, 2.8, 3.6, 1.4, "#1a3d2e", "5. İşlemi yönet\n(histogram zayıflayınca çık)"),
        (2.5, 0.6, 7, 1.3, "#222b38", "Kural: Tek başına MACD = sinyal değil, bağlam gerekir"),
    ]
    for x, y, w, h, c, txt in items:
        ax.add_patch(mpatches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.18",
            facecolor=c, edgecolor="#94a3b8", lw=1.2,
        ))
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center",
                fontsize=11, color="#f1f5f9")
    fig.savefig(OUT / "13-karar-akisi.png")
    plt.close(fig)
    print("wrote 13-karar-akisi.png")

    # gizli ıraksama (hidden bullish): fiyat HL, MACD LL — trend devam
    rng = np.random.default_rng(33)
    hidden = np.zeros(130)
    hidden[0] = 100
    for i in range(1, 130):
        if i < 40:
            hidden[i] = hidden[i - 1] + 0.55 + rng.normal(0, 0.25)
        elif i < 60:
            hidden[i] = hidden[i - 1] - 0.7 + rng.normal(0, 0.3)
        elif i < 85:
            hidden[i] = hidden[i - 1] + 0.4 + rng.normal(0, 0.25)
        elif i < 100:
            # daha yüksek dip (HL)
            hidden[i] = hidden[i - 1] - 0.35 + rng.normal(0, 0.22)
        else:
            hidden[i] = hidden[i - 1] + 0.7 + rng.normal(0, 0.28)
    # HL'yi netleştir: ikinci dip birinciden yüksek
    first_low = hidden[55:62].min()
    hidden[95:102] = np.linspace(hidden[95], first_low + 3.5, 7)
    hidden[102:] = hidden[101] + np.cumsum(np.abs(rng.normal(0.45, 0.2, 28)))
    plot_price_macd(
        hidden,
        "Gizli Bullish Iraksama — Trend Devamı (Fiyat HL, MACD LL)",
        "14-gizli-bullish-divergence.png",
        highlight=[(52, 62, "#22c55e", 0.08), (94, 104, "#22c55e", 0.08)],
    )

    print("ALL DONE ->", OUT)


if __name__ == "__main__":
    main()
