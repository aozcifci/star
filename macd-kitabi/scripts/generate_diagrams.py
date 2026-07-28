#!/usr/bin/env python3
"""Generate educational MACD diagrams for the Turkish ebook."""
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

OUT = "/workspace/macd-kitabi/gorseller"
os.makedirs(OUT, exist_ok=True)

# Color palette – deep teal / warm amber (avoid purple/cream AI clichés)
C = {
    "bg": "#0f1c24",
    "panel": "#152832",
    "grid": "#243944",
    "text": "#e8f0f4",
    "muted": "#8aa3b0",
    "macd": "#2ec4b6",      # teal
    "signal": "#f4a261",    # amber
    "hist_pos": "#3d9b7a",
    "hist_neg": "#e76f51",
    "price": "#cfe0e8",
    "zero": "#5c7a88",
    "accent": "#e9c46a",
    "bull": "#2a9d8f",
    "bear": "#e76f51",
}

plt.rcParams.update({
    "figure.facecolor": C["bg"],
    "axes.facecolor": C["panel"],
    "axes.edgecolor": C["grid"],
    "axes.labelcolor": C["text"],
    "xtick.color": C["muted"],
    "ytick.color": C["muted"],
    "text.color": C["text"],
    "grid.color": C["grid"],
    "font.family": "DejaVu Sans",
    "axes.titleweight": "bold",
})


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print("wrote", path)


def make_price_series(n=120, seed=7):
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    # Trendy then pullback then rally – readable for teaching
    base = 100 + 0.35 * t + 8 * np.sin(t / 18)
    noise = rng.normal(0, 1.2, n)
    shock = np.zeros(n)
    shock[40:55] = -np.linspace(0, 12, 15)
    shock[55:70] = -12 + np.linspace(0, 6, 15)
    shock[85:100] = np.linspace(0, 10, 15)
    price = base + noise + shock
    return t, price


def ema(series, span):
    series = np.asarray(series, dtype=float)
    alpha = 2 / (span + 1)
    out = np.empty_like(series)
    out[0] = series[0]
    for i in range(1, len(series)):
        out[i] = alpha * series[i] + (1 - alpha) * out[i - 1]
    return out


def macd_parts(price, fast=12, slow=26, signal=9):
    macd = ema(price, fast) - ema(price, slow)
    sig = ema(macd, signal)
    hist = macd - sig
    return macd, sig, hist


# 1) Anatomy: three components labeled
def fig_anatomy():
    t, price = make_price_series()
    macd, sig, hist = macd_parts(price)
    fig, axes = plt.subplots(2, 1, figsize=(11, 7.2), gridspec_kw={"height_ratios": [1.3, 1]}, sharex=True)
    axp, axm = axes
    axp.plot(t, price, color=C["price"], lw=1.8, label="Fiyat")
    axp.set_title("MACD Anatomisi — Üç Parça Birlikte", fontsize=14, pad=12)
    axp.legend(loc="upper left", frameon=False)
    axp.grid(True, alpha=0.35)
    axp.set_ylabel("Fiyat")

    colors = [C["hist_pos"] if h >= 0 else C["hist_neg"] for h in hist]
    axm.bar(t, hist, color=colors, width=0.9, alpha=0.75, label="Histogram")
    axm.plot(t, macd, color=C["macd"], lw=2.2, label="MACD çizgisi")
    axm.plot(t, sig, color=C["signal"], lw=2.0, label="Sinyal çizgisi")
    axm.axhline(0, color=C["zero"], lw=1.2, ls="--", label="Sıfır çizgisi")
    axm.legend(loc="upper left", ncol=2, frameon=False, fontsize=9)
    axm.grid(True, alpha=0.35)
    axm.set_xlabel("Zaman (bar)")
    axm.set_ylabel("MACD")
    # Callouts
    axm.annotate("MACD çizgisi", xy=(95, macd[95]), xytext=(70, macd.max()*0.85),
                 arrowprops=dict(arrowstyle="->", color=C["macd"]), color=C["macd"], fontsize=10)
    axm.annotate("Sinyal çizgisi", xy=(105, sig[105]), xytext=(78, sig.min()*0.9),
                 arrowprops=dict(arrowstyle="->", color=C["signal"]), color=C["signal"], fontsize=10)
    fig.tight_layout()
    save(fig, "01-macd-anatomi.png")


# 2) Formula / building blocks diagram
def fig_formula():
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("MACD Nasıl Hesaplanır?", fontsize=14, pad=10)

    def box(x, y, w, h, text, color, fs=11):
        r = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                           facecolor=color, edgecolor="#ffffff33", linewidth=1.2)
        ax.add_patch(r)
        ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs, color=C["bg"],
                fontweight="bold", wrap=True)

    box(0.4, 4.2, 2.6, 1.0, "12 periyotluk\nEMA (hızlı)", "#2ec4b6")
    box(3.7, 4.2, 2.6, 1.0, "26 periyotluk\nEMA (yavaş)", "#457b9d")
    box(7.0, 4.2, 2.6, 1.0, "MACD çizgisi\n= EMA12 − EMA26", "#e9c46a")
    ax.annotate("", xy=(3.6, 4.7), xytext=(3.1, 4.7),
                arrowprops=dict(arrowstyle="->", color=C["muted"], lw=2))
    ax.annotate("", xy=(6.9, 4.7), xytext=(6.4, 4.7),
                arrowprops=dict(arrowstyle="->", color=C["muted"], lw=2))
    ax.text(5.0, 3.7, "−", fontsize=22, ha="center", color=C["text"], fontweight="bold")

    box(1.5, 2.2, 3.2, 1.0, "Sinyal çizgisi\n= MACD'nin 9 EMA'sı", "#f4a261")
    box(5.5, 2.2, 3.2, 1.0, "Histogram\n= MACD − Sinyal", "#e76f51")
    ax.annotate("", xy=(3.1, 3.2), xytext=(8.0, 4.2),
                arrowprops=dict(arrowstyle="->", color=C["muted"], lw=1.6, connectionstyle="arc3,rad=0.2"))
    ax.annotate("", xy=(7.1, 3.2), xytext=(8.2, 4.2),
                arrowprops=dict(arrowstyle="->", color=C["muted"], lw=1.6, connectionstyle="arc3,rad=-0.15"))

    ax.text(5.0, 0.9, "Standart ayar: (12, 26, 9)  —  Gerald Appel, 1970'ler",
            ha="center", fontsize=11, color=C["muted"])
    ax.text(5.0, 0.35, "Kısa EMA uzun EMA'nın üstünde → MACD pozitif (boğa eğilimi)",
            ha="center", fontsize=10, color=C["bull"])
    save(fig, "02-macd-formulu.png")


# 3) Signal line crossover
def fig_crossover():
    t, price = make_price_series(seed=11)
    macd, sig, hist = macd_parts(price)
    # Find a clear bullish and bearish cross
    cross_up = None
    cross_dn = None
    for i in range(30, len(t)-5):
        if macd[i-1] < sig[i-1] and macd[i] >= sig[i] and cross_up is None:
            cross_up = i
        if macd[i-1] > sig[i-1] and macd[i] <= sig[i] and cross_dn is None and cross_up and i > cross_up + 8:
            cross_dn = i
            break

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), gridspec_kw={"height_ratios": [1.2, 1]}, sharex=True)
    axp, axm = axes
    axp.plot(t, price, color=C["price"], lw=1.7)
    axp.set_title("Sinyal Çizgisi Kesişimi — Alış / Satış Tetikleri", fontsize=14)
    axp.grid(True, alpha=0.35)
    axp.set_ylabel("Fiyat")

    axm.plot(t, macd, color=C["macd"], lw=2.2, label="MACD")
    axm.plot(t, sig, color=C["signal"], lw=2.0, label="Sinyal")
    axm.axhline(0, color=C["zero"], lw=1, ls="--")
    axm.grid(True, alpha=0.35)
    axm.legend(loc="upper left", frameon=False)
    axm.set_xlabel("Zaman")
    axm.set_ylabel("MACD")

    if cross_up:
        for ax in axes:
            ax.axvline(cross_up, color=C["bull"], ls=":", lw=1.5, alpha=0.8)
        axm.scatter([cross_up], [macd[cross_up]], color=C["bull"], s=80, zorder=5)
        axm.annotate("Boğa kesişimi\n(MACD ↑ sinyal)", xy=(cross_up, macd[cross_up]),
                     xytext=(cross_up-28, macd[cross_up]+abs(macd).max()*0.25),
                     color=C["bull"], fontsize=10,
                     arrowprops=dict(arrowstyle="->", color=C["bull"]))
        axp.annotate("Alış bölgesi", xy=(cross_up, price[cross_up]),
                     xytext=(cross_up+5, price[cross_up]+8), color=C["bull"], fontsize=10,
                     arrowprops=dict(arrowstyle="->", color=C["bull"]))
    if cross_dn:
        for ax in axes:
            ax.axvline(cross_dn, color=C["bear"], ls=":", lw=1.5, alpha=0.8)
        axm.scatter([cross_dn], [macd[cross_dn]], color=C["bear"], s=80, zorder=5)
        axm.annotate("Ayı kesişimi\n(MACD ↓ sinyal)", xy=(cross_dn, macd[cross_dn]),
                     xytext=(cross_dn+5, macd[cross_dn]-abs(macd).max()*0.35),
                     color=C["bear"], fontsize=10,
                     arrowprops=dict(arrowstyle="->", color=C["bear"]))
        axp.annotate("Satış bölgesi", xy=(cross_dn, price[cross_dn]),
                     xytext=(cross_dn+5, price[cross_dn]-10), color=C["bear"], fontsize=10,
                     arrowprops=dict(arrowstyle="->", color=C["bear"]))
    fig.tight_layout()
    save(fig, "03-sinyal-kesisimi.png")


# 4) Zero line
def fig_zero():
    t, price = make_price_series(seed=3)
    macd, sig, hist = macd_parts(price)
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True, gridspec_kw={"height_ratios": [1.2, 1]})
    axp, axm = axes
    axp.plot(t, price, color=C["price"], lw=1.7)
    axp.set_title("Sıfır Çizgisi — Trend Eğiliminin Haritası", fontsize=14)
    axp.grid(True, alpha=0.35)

    axm.fill_between(t, macd, 0, where=(macd >= 0), color=C["bull"], alpha=0.25, label="MACD > 0 (boğa eğilim)")
    axm.fill_between(t, macd, 0, where=(macd < 0), color=C["bear"], alpha=0.25, label="MACD < 0 (ayı eğilim)")
    axm.plot(t, macd, color=C["macd"], lw=2.2)
    axm.plot(t, sig, color=C["signal"], lw=1.5, alpha=0.85)
    axm.axhline(0, color=C["accent"], lw=1.8)
    axm.legend(loc="upper left", frameon=False, fontsize=9)
    axm.grid(True, alpha=0.35)
    axm.set_xlabel("Zaman")
    axm.text(0.02, 0.92, "Sıfırın üstü: kısa EMA > uzun EMA", transform=axm.transAxes,
             color=C["bull"], fontsize=10)
    axm.text(0.02, 0.05, "Sıfırın altı: kısa EMA < uzun EMA", transform=axm.transAxes,
             color=C["bear"], fontsize=10)
    fig.tight_layout()
    save(fig, "04-sifir-cizgisi.png")


# 5) Histogram acceleration
def fig_histogram():
    t = np.arange(60)
    # Craft a clear acceleration / deceleration story
    macd = np.concatenate([
        np.linspace(-2, -0.5, 15),
        np.linspace(-0.5, 2.5, 20),
        np.linspace(2.5, 1.0, 15),
        np.linspace(1.0, -1.5, 10),
    ])
    sig = ema(macd, 9)
    hist = macd - sig
    fig, ax = plt.subplots(figsize=(11, 5.2))
    colors = []
    for i, h in enumerate(hist):
        if h >= 0:
            colors.append("#2a9d8f" if i == 0 or h >= hist[i-1] else "#7dcfb6")
        else:
            colors.append("#e76f51" if i == 0 or h <= hist[i-1] else "#f4a698")
    ax.bar(t, hist, color=colors, width=0.85, alpha=0.9)
    ax.plot(t, macd, color=C["macd"], lw=2.2, label="MACD")
    ax.plot(t, sig, color=C["signal"], lw=2.0, label="Sinyal")
    ax.axhline(0, color=C["zero"], ls="--")
    ax.set_title("Histogram: Momentum Hızlanıyor mu, Yavaşlıyor mu?", fontsize=14)
    ax.legend(loc="upper left", frameon=False)
    ax.grid(True, alpha=0.35)
    ax.annotate("Barlar büyüyor\n→ momentum hızlanıyor", xy=(25, hist[25]),
                xytext=(8, max(hist)*0.9), color=C["bull"], fontsize=10,
                arrowprops=dict(arrowstyle="->", color=C["bull"]))
    ax.annotate("Barlar küçülüyor\n→ momentum zayıflıyor", xy=(42, hist[42]),
                xytext=(45, max(hist)*0.7), color=C["accent"], fontsize=10,
                arrowprops=dict(arrowstyle="->", color=C["accent"]))
    ax.set_xlabel("Zaman")
    ax.set_ylabel("Değer")
    fig.tight_layout()
    save(fig, "05-histogram-okuma.png")


# 6) Bullish divergence
def fig_divergence_bull():
    t = np.arange(80)
    # Price makes lower low; MACD makes higher low
    price = np.concatenate([
        np.linspace(110, 95, 25) + np.sin(np.linspace(0, 6, 25))*1.5,
        np.linspace(95, 88, 25) + np.sin(np.linspace(0, 5, 25)),
        np.linspace(88, 102, 30) + np.sin(np.linspace(0, 4, 30)),
    ])
    # Synthetic MACD-like oscillator with higher low
    osc = np.concatenate([
        np.linspace(-0.5, -2.2, 25),
        np.linspace(-2.2, -1.2, 25),
        np.linspace(-1.2, 1.5, 30),
    ])
    sig = ema(osc, 9)
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True, gridspec_kw={"height_ratios": [1.25, 1]})
    axp, axm = axes
    axp.plot(t, price, color=C["price"], lw=2)
    # mark lows
    low1, low2 = 24, 49
    axp.scatter([low1, low2], [price[low1], price[low2]], color=C["bear"], s=70, zorder=5)
    axp.plot([low1, low2], [price[low1], price[low2]], color=C["bear"], lw=1.8, ls="--")
    axp.annotate("Daha düşük dip", xy=(low2, price[low2]), xytext=(low2+5, price[low2]-4),
                 color=C["bear"], fontsize=10)
    axp.set_title("Boğa Uyumsuzluğu (Bullish Divergence)", fontsize=14)
    axp.grid(True, alpha=0.35)
    axp.set_ylabel("Fiyat")

    axm.plot(t, osc, color=C["macd"], lw=2.2, label="MACD")
    axm.plot(t, sig, color=C["signal"], lw=1.6, alpha=0.8)
    axm.axhline(0, color=C["zero"], ls="--")
    axm.scatter([low1, low2], [osc[low1], osc[low2]], color=C["bull"], s=70, zorder=5)
    axm.plot([low1, low2], [osc[low1], osc[low2]], color=C["bull"], lw=1.8, ls="--")
    axm.annotate("Daha yüksek dip\n(momentum güçleniyor)", xy=(low2, osc[low2]),
                 xytext=(low2+3, osc[low2]+1.2), color=C["bull"], fontsize=10,
                 arrowprops=dict(arrowstyle="->", color=C["bull"]))
    axm.grid(True, alpha=0.35)
    axm.legend(loc="upper left", frameon=False)
    axm.set_xlabel("Zaman")
    fig.tight_layout()
    save(fig, "06-boga-uyumsuzluk.png")


# 7) Bearish divergence
def fig_divergence_bear():
    t = np.arange(80)
    price = np.concatenate([
        np.linspace(90, 108, 25) + np.sin(np.linspace(0, 5, 25)),
        np.linspace(108, 118, 25) + np.sin(np.linspace(0, 4, 25))*0.8,
        np.linspace(118, 100, 30) + np.sin(np.linspace(0, 5, 30)),
    ])
    osc = np.concatenate([
        np.linspace(0.2, 2.4, 25),
        np.linspace(2.4, 1.3, 25),
        np.linspace(1.3, -1.2, 30),
    ])
    sig = ema(osc, 9)
    hi1, hi2 = 24, 49
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True, gridspec_kw={"height_ratios": [1.25, 1]})
    axp, axm = axes
    axp.plot(t, price, color=C["price"], lw=2)
    axp.scatter([hi1, hi2], [price[hi1], price[hi2]], color=C["bull"], s=70, zorder=5)
    axp.plot([hi1, hi2], [price[hi1], price[hi2]], color=C["bull"], lw=1.8, ls="--")
    axp.annotate("Daha yüksek tepe", xy=(hi2, price[hi2]), xytext=(hi2+4, price[hi2]+3),
                 color=C["bull"], fontsize=10)
    axp.set_title("Ayı Uyumsuzluğu (Bearish Divergence)", fontsize=14)
    axp.grid(True, alpha=0.35)

    axm.plot(t, osc, color=C["macd"], lw=2.2, label="MACD")
    axm.plot(t, sig, color=C["signal"], lw=1.6, alpha=0.8)
    axm.axhline(0, color=C["zero"], ls="--")
    axm.scatter([hi1, hi2], [osc[hi1], osc[hi2]], color=C["bear"], s=70, zorder=5)
    axm.plot([hi1, hi2], [osc[hi1], osc[hi2]], color=C["bear"], lw=1.8, ls="--")
    axm.annotate("Daha düşük tepe\n(momentum zayıflıyor)", xy=(hi2, osc[hi2]),
                 xytext=(hi2+3, osc[hi2]-1.5), color=C["bear"], fontsize=10,
                 arrowprops=dict(arrowstyle="->", color=C["bear"]))
    axm.grid(True, alpha=0.35)
    axm.legend(loc="upper left", frameon=False)
    fig.tight_layout()
    save(fig, "07-ayi-uyumsuzluk.png")


# 8) Convergence / divergence concept illustration
def fig_convergence_concept():
    t = np.arange(100)
    ema12 = 100 + 10*np.sin(t/12) + 0.15*t
    ema26 = 100 + 6*np.sin(t/12 - 0.8) + 0.12*t
    # force converge then diverge
    gap = ema12 - ema26
    fig, axes = plt.subplots(2, 1, figsize=(11, 6.5), sharex=True, gridspec_kw={"height_ratios": [1.3, 1]})
    ax1, ax2 = axes
    ax1.plot(t, ema12, color=C["macd"], lw=2.2, label="EMA 12 (hızlı)")
    ax1.plot(t, ema26, color=C["signal"], lw=2.2, label="EMA 26 (yavaş)")
    ax1.fill_between(t, ema12, ema26, alpha=0.15, color=C["accent"])
    ax1.set_title("Yakınsama ve Iraksama — İsmin Anlamı", fontsize=14)
    ax1.legend(loc="upper left", frameon=False)
    ax1.grid(True, alpha=0.35)
    # annotate regions
    ax1.annotate("Yakınsama\n(çizgiler birbirine yaklaşıyor)", xy=(35, (ema12[35]+ema26[35])/2),
                 xytext=(10, ema12.max()-2), color=C["muted"], fontsize=9,
                 arrowprops=dict(arrowstyle="->", color=C["muted"]))
    ax1.annotate("Iraksama\n(çizgiler uzaklaşıyor)", xy=(75, (ema12[75]+ema26[75])/2),
                 xytext=(55, ema12.min()+1), color=C["muted"], fontsize=9,
                 arrowprops=dict(arrowstyle="->", color=C["muted"]))

    ax2.plot(t, gap, color=C["accent"], lw=2.3, label="MACD = EMA12 − EMA26")
    ax2.axhline(0, color=C["zero"], ls="--")
    ax2.fill_between(t, gap, 0, where=(gap>=0), color=C["bull"], alpha=0.2)
    ax2.fill_between(t, gap, 0, where=(gap<0), color=C["bear"], alpha=0.2)
    ax2.legend(loc="upper left", frameon=False)
    ax2.grid(True, alpha=0.35)
    ax2.set_xlabel("Zaman")
    ax2.set_ylabel("Fark")
    fig.tight_layout()
    save(fig, "08-yakinsama-iraksama.png")


# 9) Strategy map – multipanel simple decision
def fig_strategy_map():
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_title("Pratik Karar Haritası (Giriş–Orta Seviye)", fontsize=14, pad=12)

    def card(x, y, w, h, title, body, edge):
        r = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.2",
                           facecolor="#1a303c", edgecolor=edge, linewidth=2)
        ax.add_patch(r)
        ax.text(x+0.25, y+h-0.45, title, fontsize=12, fontweight="bold", color=edge, ha="left")
        ax.text(x+0.25, y+0.35, body, fontsize=9.5, color=C["text"], ha="left", va="bottom")

    card(0.4, 4.5, 5.3, 2.8, "1) Sinyal kesişimi",
         "MACD, sinyalin üstüne çıkarsa alış\nadayı. Altına inerse satış adayı.\nTrend yönüyle aynı yönde işlem al.",
         C["macd"])
    card(6.3, 4.5, 5.3, 2.8, "2) Sıfır çizgisi filtresi",
         "Sıfırın üstünde boğa kesişimleri\ndaha güvenilir. Sıfırın altında ayı\nkesişimleri daha anlamlıdır.",
         C["accent"])
    card(0.4, 0.6, 5.3, 3.2, "3) Histogram teyidi",
         "Barlar sıfıra doğru küçülüyorsa\nmomentum zayıflıyor olabilir.\nKesişim öncesi erken uyarıdır;\nteyit için kesişimi bekle.",
         C["signal"])
    card(6.3, 0.6, 5.3, 3.2, "4) Uyumsuzluk + teyit",
         "Fiyat yeni dip/tepe yapıyor ama\nMACD yapmıyorsa dikkat.\nTek başına işlem açma; kesişim\nveya destek/direnç ile teyit et.",
         C["bear"])
    save(fig, "09-strateji-haritasi.png")


# 10) Timeframes comparison
def fig_timeframes():
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.set_title("Zaman Dilimi Seçimi — Aynı MACD, Farklı Hikâye", fontsize=14)

    rows = [
        (3.6, "Scalp / kısa vadeli", "1–5 dk", "Daha hızlı ayarlar\n(örn. 5-13-5) denenebilir", C["bear"]),
        (2.4, "Gün içi", "15 dk – 1 saat", "Standart 12-26-9\ngenelde yeterli", C["signal"]),
        (1.2, "Swing", "4 saat – günlük", "En dengeli sinyal/gürültü\noranı buradadır", C["macd"]),
        (0.0, "Pozisyon / yatırım", "Haftalık", "Az sinyal, güçlü eğilim\nokuması", C["accent"]),
    ]
    headers = [(0.3, "Stil"), (2.8, "Grafik"), (5.0, "Not")]
    for x, h in headers:
        ax.text(x, 4.5, h, fontsize=11, color=C["muted"], fontweight="bold")
    for y, stil, grafik, not_, col in rows:
        ax.add_patch(FancyBboxPatch((0.2, y+0.15), 9.5, 1.0,
                     boxstyle="round,pad=0.02,rounding_size=0.12",
                     facecolor="#1a303c", edgecolor=col, lw=1.5))
        ax.text(0.4, y+0.65, stil, fontsize=11, color=C["text"], va="center")
        ax.text(2.8, y+0.65, grafik, fontsize=11, color=col, va="center", fontweight="bold")
        ax.text(5.0, y+0.65, not_.replace("\n", " "), fontsize=10, color=C["muted"], va="center")
    save(fig, "10-zaman-dilimleri.png")


# 11) Cover visual
def fig_cover():
    t, price = make_price_series(n=140, seed=21)
    macd, sig, hist = macd_parts(price)
    fig = plt.figure(figsize=(11, 7))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 140)
    # stylized background waves
    ax.fill_between(t, 0, hist*8 + 20, color=C["hist_pos"], alpha=0.15)
    colors = [C["hist_pos"] if h >= 0 else C["hist_neg"] for h in hist]
    ax.bar(t, hist*6 + 18, color=colors, width=1.0, alpha=0.35)
    ax.plot(t, macd*6 + 18, color=C["macd"], lw=3)
    ax.plot(t, sig*6 + 18, color=C["signal"], lw=2.5)
    ax.axis("off")
    ax.text(70, 38, "SİNYALİN RİTMİ", ha="center", va="center",
            fontsize=36, fontweight="bold", color=C["text"],
            fontfamily="DejaVu Sans")
    ax.text(70, 32, "MACD'yi Sade Anlatım", ha="center", va="center",
            fontsize=18, color=C["macd"])
    ax.text(70, 27, "Giriş ve orta seviye için görsel rehber", ha="center",
            fontsize=12, color=C["muted"])
    save(fig, "00-kapak.png")


# 12) Common mistakes
def fig_mistakes():
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.set_title("Sık Yapılan Hatalar — Kısa Hatırlatma", fontsize=14)
    items = [
        (0.4, 3.8, "Her kesişimi işlem sanmak", "Yatay piyasada MACD sık\nyanlış sinyal üretir."),
        (5.2, 3.8, "Tek göstergeyle karar", "Fiyat yapısı, hacim veya\nRSI ile teyit et."),
        (0.4, 0.7, "Gecikmeyi unutmak", "MACD gecikmeli bir göstergedir;\ngeç giriş riskini yönet."),
        (5.2, 0.7, "Ayarları sürekli değiştirmek", "Bir ayar seç, uzun süre\ntest et, sonra karar ver."),
    ]
    for x, y, title, body in items:
        ax.add_patch(FancyBboxPatch((x, y), 4.4, 2.2,
                     boxstyle="round,pad=0.04,rounding_size=0.18",
                     facecolor="#1a303c", edgecolor="#e76f5188", lw=1.5))
        ax.text(x+0.3, y+1.55, "✗  " + title, fontsize=12, color=C["bear"], fontweight="bold")
        ax.text(x+0.3, y+0.55, body, fontsize=11, color=C["text"])
    save(fig, "11-sik-hatalar.png")


if __name__ == "__main__":
    fig_cover()
    fig_anatomy()
    fig_formula()
    fig_crossover()
    fig_zero()
    fig_histogram()
    fig_divergence_bull()
    fig_divergence_bear()
    fig_convergence_concept()
    fig_strategy_map()
    fig_timeframes()
    fig_mistakes()
    print("done")
