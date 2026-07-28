#!/usr/bin/env python3
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Arc

OUT = "/workspace/macd-kitabi/gorseller"
os.makedirs(OUT, exist_ok=True)

C = {
    "bg": "#0f1c24", "panel": "#152832", "grid": "#243944", "text": "#e8f0f4",
    "muted": "#8aa3b0", "macd": "#2ec4b6", "signal": "#f4a261", "hist_pos": "#3d9b7a",
    "hist_neg": "#e76f51", "price": "#cfe0e8", "zero": "#5c7a88", "accent": "#e9c46a",
    "bull": "#2a9d8f", "bear": "#e76f51",
}
plt.rcParams.update({
    "figure.facecolor": C["bg"], "axes.facecolor": C["panel"], "axes.edgecolor": C["grid"],
    "axes.labelcolor": C["text"], "xtick.color": C["muted"], "ytick.color": C["muted"],
    "text.color": C["text"], "grid.color": C["grid"], "font.family": "DejaVu Sans",
    "axes.titleweight": "bold",
})

def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print("wrote", name)

def ema(series, span):
    series = np.asarray(series, dtype=float)
    alpha = 2 / (span + 1)
    out = np.empty_like(series); out[0] = series[0]
    for i in range(1, len(series)):
        out[i] = alpha * series[i] + (1 - alpha) * out[i - 1]
    return out

def macd_parts(price, fast=12, slow=26, signal=9):
    m = ema(price, fast) - ema(price, slow)
    s = ema(m, signal)
    return m, s, m - s

# 12 SMA vs EMA
def fig_sma_ema():
    t = np.arange(80)
    price = 100 + np.cumsum(np.random.default_rng(2).normal(0, 1.1, 80)) + np.linspace(0, 8, 80)
    sma = np.convolve(price, np.ones(10)/10, mode='same')
    e = ema(price, 10)
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(t, price, color=C["price"], lw=1.5, label="Fiyat", alpha=0.85)
    ax.plot(t, sma, color=C["signal"], lw=2, label="SMA 10")
    ax.plot(t, e, color=C["macd"], lw=2, label="EMA 10")
    ax.set_title("SMA vs EMA — Hangisi Daha Çabuk Tepki Verir?")
    ax.legend(frameon=False); ax.grid(True, alpha=0.35)
    ax.annotate("EMA daha hızlı uyum sağlar", xy=(55, e[55]), xytext=(35, e.max()+2),
                color=C["macd"], arrowprops=dict(arrowstyle="->", color=C["macd"]))
    save(fig, "12-sma-vs-ema.png")

# 13 Trend vs range regimes
def fig_regimes():
    rng = np.random.default_rng(5)
    t = np.arange(150)
    trend = 100 + 0.25*t + rng.normal(0, 0.8, 150)
    rang = 100 + 4*np.sin(t/6) + rng.normal(0, 0.6, 150)
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex='col')
    axes[0,0].plot(t, trend, color=C["price"]); axes[0,0].set_title("Trend piyasası — fiyat")
    m,s,h = macd_parts(trend)
    axes[1,0].plot(t, m, C["macd"]); axes[1,0].plot(t, s, C["signal"]); axes[1,0].axhline(0, color=C["zero"], ls="--")
    axes[1,0].set_title("Trend'de MACD daha temiz")
    axes[0,1].plot(t, rang, color=C["price"]); axes[0,1].set_title("Yatay (range) piyasa — fiyat")
    m2,s2,_ = macd_parts(rang)
    axes[1,1].plot(t, m2, C["macd"]); axes[1,1].plot(t, s2, C["signal"]); axes[1,1].axhline(0, color=C["zero"], ls="--")
    axes[1,1].set_title("Range'de MACD sık kesişim (gürültü)")
    for ax in axes.ravel(): ax.grid(True, alpha=0.3)
    fig.suptitle("Piyasa Rejimi MACD Kalitesini Belirler", fontsize=14, color=C["text"])
    fig.tight_layout(); save(fig, "13-piyasa-rejimleri.png")

# 14 Hidden bullish divergence
def fig_hidden_bull():
    t = np.arange(70)
    price = np.concatenate([np.linspace(90, 110, 25), np.linspace(110, 100, 20), np.linspace(100, 120, 25)])
    osc = np.concatenate([np.linspace(-1, 2, 25), np.linspace(2, -0.5, 20), np.linspace(-0.5, 2.5, 25)])
    # hidden bull: price higher low, macd lower low during uptrend pullback
    price[35:50] = np.linspace(110, 104, 15)  # higher low vs earlier? simplify labels
    fig, axes = plt.subplots(2,1,figsize=(10,6.5), sharex=True, gridspec_kw={"height_ratios":[1.2,1]})
    axes[0].plot(t, price, C["price"], lw=2)
    axes[0].set_title("Gizli Boğa Uyumsuzluğu (Hidden Bullish) — Trend Devamı İpucu")
    l1,l2 = 20, 48
    axes[0].scatter([l1,l2],[price[l1],price[l2]], color=C["bull"], s=60)
    axes[0].plot([l1,l2],[price[l1],price[l2]], C["bull"], ls="--")
    axes[0].annotate("Daha yüksek dip (fiyat)", xy=(l2, price[l2]), xytext=(l2-25, price[l2]-8), color=C["bull"])
    axes[1].plot(t, osc, C["macd"], lw=2); axes[1].axhline(0, color=C["zero"], ls="--")
    axes[1].scatter([l1,l2],[osc[l1],osc[l2]], color=C["bear"], s=60)
    axes[1].plot([l1,l2],[osc[l1],osc[l2]], C["bear"], ls="--")
    axes[1].annotate("Daha düşük dip (MACD)", xy=(l2, osc[l2]), xytext=(l2-20, osc[l2]-1.2), color=C["bear"])
    for ax in axes: ax.grid(True, alpha=0.3)
    fig.tight_layout(); save(fig, "14-gizli-boga-uyumsuzluk.png")

# 15 Hidden bearish
def fig_hidden_bear():
    t = np.arange(70)
    price = np.concatenate([np.linspace(120, 100, 25), np.linspace(100, 108, 20), np.linspace(108, 85, 25)])
    osc = np.concatenate([np.linspace(1.5, -2, 25), np.linspace(-2, 0.8, 20), np.linspace(0.8, -2.5, 25)])
    fig, axes = plt.subplots(2,1,figsize=(10,6.5), sharex=True, gridspec_kw={"height_ratios":[1.2,1]})
    axes[0].plot(t, price, C["price"], lw=2)
    axes[0].set_title("Gizli Ayı Uyumsuzluğu (Hidden Bearish) — Düşüş Devamı İpucu")
    h1,h2 = 20, 48
    axes[0].scatter([h1,h2],[price[h1],price[h2]], color=C["bear"], s=60)
    axes[0].plot([h1,h2],[price[h1],price[h2]], C["bear"], ls="--")
    axes[0].annotate("Daha düşük tepe (fiyat)", xy=(h2,price[h2]), xytext=(h2-25, price[h2]+8), color=C["bear"])
    axes[1].plot(t, osc, C["macd"], lw=2); axes[1].axhline(0, color=C["zero"], ls="--")
    axes[1].scatter([h1,h2],[osc[h1],osc[h2]], color=C["bull"], s=60)
    axes[1].plot([h1,h2],[osc[h1],osc[h2]], C["bull"], ls="--")
    axes[1].annotate("Daha yüksek tepe (MACD)", xy=(h2,osc[h2]), xytext=(h2-22, osc[h2]+1.2), color=C["bull"])
    for ax in axes: ax.grid(True, alpha=0.3)
    fig.tight_layout(); save(fig, "15-gizli-ayi-uyumsuzluk.png")

# 16 Settings comparison
def fig_settings():
    rng = np.random.default_rng(9)
    t = np.arange(120)
    price = 100 + np.cumsum(rng.normal(0.05, 1.0, 120))
    fig, axes = plt.subplots(3,1,figsize=(10,8), sharex=True)
    axes[0].plot(t, price, C["price"], lw=1.5); axes[0].set_title("Aynı Fiyat — Farklı MACD Ayarları")
    axes[0].grid(True, alpha=0.3)
    for ax, (f,s,sig), title, col in [
        (axes[1], (5,13,5), "Hızlı 5-13-5", C["bear"]),
        (axes[2], (12,26,9), "Klasik 12-26-9", C["macd"]),
    ]:
        m, sg, _ = macd_parts(price, f, s, sig)
        ax.plot(t, m, col, lw=2, label="MACD"); ax.plot(t, sg, C["signal"], lw=1.5, label="Sinyal")
        ax.axhline(0, color=C["zero"], ls="--"); ax.set_ylabel(title); ax.legend(frameon=False, loc="upper left")
        ax.grid(True, alpha=0.3)
    fig.tight_layout(); save(fig, "16-ayar-karsilastirma.png")

# 17 Risk reward sketch
def fig_risk():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0,10); ax.set_ylim(0,6); ax.axis("off")
    ax.set_title("MACD Girişinde Risk / Ödül İskeleti", fontsize=14)
    # price path
    xs = np.linspace(1,9,50); ys = 2.2 + 0.05*(xs-1)**2
    ax.plot(xs, ys, color=C["price"], lw=2.5)
    entry, stop, t1, t2 = 3.5, 1.3, 3.5, 4.8
    ax.axhline(entry, color=C["macd"], ls="--", xmin=0.3, xmax=0.9)
    ax.axhline(stop, color=C["bear"], ls="--", xmin=0.3, xmax=0.9)
    ax.axhline(t1+0.7, color=C["accent"], ls="--", xmin=0.3, xmax=0.9)
    ax.axhline(t2, color=C["gold"] if "gold" in C else C["accent"], ls=":", xmin=0.3, xmax=0.9)
    ax.text(9.2, entry, "Giriş", color=C["macd"], va="center")
    ax.text(9.2, stop, "Stop", color=C["bear"], va="center")
    ax.text(9.2, entry+0.7, "Hedef 1 (1.5R)", color=C["accent"], va="center")
    ax.text(9.2, t2, "Hedef 2 (2.5R)", color=C["accent"], va="center")
    ax.annotate("", xy=(2.2, entry), xytext=(2.2, stop), arrowprops=dict(arrowstyle="<->", color=C["bear"]))
    ax.text(1.3, (entry+stop)/2, "1R\nrisk", color=C["bear"], ha="center", fontsize=10)
    ax.text(5, 0.5, "Kural: Sinyal güzel olsa bile R tanımsızsa işlem yok.", color=C["muted"], ha="center")
    save(fig, "17-risk-odul.png")

# 18 Checklist poster
def fig_checklist():
    fig, ax = plt.subplots(figsize=(10, 6)); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0,7)
    ax.set_title("İşlem Öncesi MACD Kontrol Listesi", fontsize=14)
    items = [
        "1. Piyasa rejimi: trend mi, range mi?",
        "2. Üst zaman dilimi bias (sıfır çizgisi) nedir?",
        "3. Sinyal, bias ile aynı yönde mi?",
        "4. Histogram tempo artıyor mu, tükeniyor mu?",
        "5. Destek/direnç / yapı ile uyumlu mu?",
        "6. Stop yeri net mi? Risk hesabı yapıldı mı?",
        "7. Hedef mantıklı mı? (en az ~1.5R)",
        "8. Bugün işlem kotası / psikoloji uygun mu?",
    ]
    for i, it in enumerate(items):
        y = 6.1 - i*0.7
        ax.add_patch(FancyBboxPatch((0.5, y-0.25), 9, 0.55, boxstyle="round,pad=0.02,rounding_size=0.1",
                                    facecolor="#1a303c", edgecolor=C["macd"] if i%2==0 else C["accent"], lw=1.2))
        ax.text(0.8, y, it, va="center", fontsize=12)
    save(fig, "18-kontrol-listesi.png")

# 19 MTF stack
def fig_mtf():
    fig, axes = plt.subplots(3,1,figsize=(10,7.5), sharex=False)
    rng = np.random.default_rng(1)
    for ax, n, title, seed in [
        (axes[0], 60, "Haftalık bias", 1),
        (axes[1], 90, "Günlük giriş arama", 2),
        (axes[2], 120, "4 saat zamanlama", 3),
    ]:
        r = np.random.default_rng(seed)
        p = 100 + np.cumsum(r.normal(0.08, 1.0, n))
        m,s,_ = macd_parts(p)
        ax.plot(m, C["macd"], lw=2); ax.plot(s, C["signal"], lw=1.5); ax.axhline(0, color=C["zero"], ls="--")
        ax.set_ylabel(title); ax.grid(True, alpha=0.3)
        side = "BOĞA" if m[-1] > 0 else "AYI"
        ax.text(0.98, 0.85, side, transform=ax.transAxes, ha="right", color=C["bull"] if side=="BOĞA" else C["bear"], fontweight="bold")
    axes[0].set_title("Çoklu Zaman Dilimi (MTF) — Üstten Alta Hizalama")
    fig.tight_layout(); save(fig, "19-mtf-hizalama.png")

# 20 False signals gallery
def fig_false():
    rng = np.random.default_rng(4)
    t = np.arange(100)
    price = 100 + 3*np.sin(t/5) + rng.normal(0, 0.4, 100)
    m,s,h = macd_parts(price)
    crosses = [i for i in range(1,len(m)) if (m[i-1]-s[i-1])*(m[i]-s[i]) <= 0]
    fig, axes = plt.subplots(2,1,figsize=(10,6.5), sharex=True, gridspec_kw={"height_ratios":[1.1,1]})
    axes[0].plot(t, price, C["price"]); axes[0].set_title(f"Yanlış Sinyal Galerisi — {len(crosses)} kesişim, az trend")
    axes[1].plot(t, m, C["macd"]); axes[1].plot(t, s, C["signal"]); axes[1].axhline(0, color=C["zero"], ls="--")
    for c in crosses:
        axes[1].axvline(c, color=C["bear"], alpha=0.25, lw=1)
    axes[1].text(0.02, 0.9, "Her dikey çizgi bir kesişim = çoğu gürültü", transform=axes[1].transAxes, color=C["bear"])
    for ax in axes: ax.grid(True, alpha=0.3)
    fig.tight_layout(); save(fig, "20-yanlis-sinyaller.png")

# 21 Elder impulse idea
def fig_impulse():
    t = np.arange(80)
    price = 100 + np.cumsum(np.random.default_rng(8).normal(0.05, 0.9, 80))
    m,s,h = macd_parts(price)
    e13 = ema(price, 13)
    colors = []
    for i in range(len(price)):
        up = e13[i] > (e13[i-1] if i else e13[i]) and h[i] > (h[i-1] if i else h[i])
        dn = e13[i] < (e13[i-1] if i else e13[i]) and h[i] < (h[i-1] if i else h[i])
        colors.append(C["bull"] if up else (C["bear"] if dn else C["accent"]))
    fig, ax = plt.subplots(figsize=(10,4.8))
    for i in range(1, len(t)):
        ax.plot(t[i-1:i+1], price[i-1:i+1], color=colors[i], lw=2.4)
    ax.set_title("Impulse Fikri — EMA yönü + histogram yönü (renkli fiyat)")
    ax.grid(True, alpha=0.3)
    ax.text(0.02, 0.92, "Yeşil: ikisi yukarı  |  Kırmızı: ikisi aşağı  |  Amber: karışık", transform=ax.transAxes, color=C["muted"], fontsize=9)
    save(fig, "21-impulse-renk.png")

# 22 Learning path
def fig_path():
    fig, ax = plt.subplots(figsize=(10, 5)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 5)
    ax.set_title("Öğrenme Yolu — 4 Durak", fontsize=14)
    stops = [(0.5,"1. Temel","EMA, MACD anatomi"), (3.3,"2. Okuma","Kesişim, sıfır, hist."),
             (6.1,"3. Filtre","Rejim, MTF, teyit"), (8.9,"4. Uygulama","Strateji, risk, günce")]
    for i,(x,t1,t2) in enumerate(stops):
        ax.add_patch(FancyBboxPatch((x, 1.5), 2.4, 2.2, boxstyle="round,pad=0.04,rounding_size=0.2",
                                    facecolor="#1a303c", edgecolor=C["macd"], lw=2))
        ax.text(x+1.2, 3.1, t1, ha="center", fontsize=13, fontweight="bold", color=C["macd"])
        ax.text(x+1.2, 2.2, t2, ha="center", fontsize=10, color=C["text"])
        if i < 3:
            ax.annotate("", xy=(x+2.6, 2.6), xytext=(x+2.4, 2.6), arrowprops=dict(arrowstyle="->", color=C["accent"], lw=2))
    save(fig, "22-ogrenme-yolu.png")

# 23 Histogram phases
def fig_hist_phases():
    t = np.arange(48)
    hist = np.array([*-np.linspace(0.2, 2.0, 8), *np.linspace(-2.0, -0.3, 8), *np.linspace(-0.3, 2.2, 12), *np.linspace(2.2, 0.2, 12), *np.linspace(0.2, -1.5, 8)])
    fig, ax = plt.subplots(figsize=(10,4.5))
    colors = [C["hist_pos"] if h>=0 else C["hist_neg"] for h in hist]
    ax.bar(t, hist, color=colors, width=0.85)
    ax.axhline(0, color=C["zero"], ls="--")
    ax.set_title("Histogramın 4 Fazı")
    # phase labels
    for x, lab, col in [(4,"1. Negatif\nderinleşme", C["bear"]), (12,"2. Toparlanma", C["accent"]),
                        (24,"3. Pozitif\nbüyüme", C["bull"]), (38,"4. Zayıflama", C["signal"])]:
        ax.text(x, max(hist)*0.85 if hist[x]>0 else min(hist)*0.85, lab, ha="center", color=col, fontsize=9)
    ax.grid(True, alpha=0.3); save(fig, "23-histogram-fazlari.png")

# 24 Comparison MACD RSI
def fig_macd_rsi():
    fig, ax = plt.subplots(figsize=(10,5)); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0,6)
    ax.set_title("MACD vs RSI — Ne Zaman Hangisi?", fontsize=14)
    def colbox(x, title, lines, edge):
        ax.add_patch(FancyBboxPatch((x, 0.6), 4.3, 4.6, boxstyle="round,pad=0.05,rounding_size=0.2",
                                    facecolor="#1a303c", edgecolor=edge, lw=2))
        ax.text(x+2.15, 4.7, title, ha="center", fontsize=14, fontweight="bold", color=edge)
        for i,l in enumerate(lines):
            ax.text(x+0.3, 4.1 - i*0.55, "• "+l, fontsize=11, color=C["text"])
    colbox(0.5, "MACD", ["Trend + momentum hibriti","Sıfır çizgisi bias verir","Kesişim / hist. odaklı","Trendli piyasada güçlü","Range'de gürültülü olabilir"], C["macd"])
    colbox(5.2, "RSI", ["0–100 osilatör","Aşırı alım/satım vurgusu","Uyumsuzluk için popüler","Range'de daha kullanışlı","Tek başına trend vermez"], C["signal"])
    save(fig, "24-macd-vs-rsi.png")

# 25 Weekly plan
def fig_week():
    fig, ax = plt.subplots(figsize=(10,5)); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0,6)
    ax.set_title("7 Günlük MACD Pratik Planı", fontsize=14)
    days = [("Pzt","Sadece izle\nanatomiyi işaretle"),("Sal","Kesişim günlüğü"),("Çar","Sıfır çizgisi bias"),
            ("Per","Histogram tempo"),("Cum","Uyumsuzluk avı"),("Cmt","MTF hizalama"),("Paz","Haftalık özet")]
    for i,(d,t) in enumerate(days):
        x = 0.35 + i*1.35
        ax.add_patch(FancyBboxPatch((x, 1.5), 1.2, 3.2, boxstyle="round,pad=0.03,rounding_size=0.15",
                                    facecolor="#1a303c", edgecolor=C["accent"] if i%2 else C["macd"], lw=1.5))
        ax.text(x+0.6, 4.3, d, ha="center", fontweight="bold", color=C["gold"] if False else C["accent"])
        ax.text(x+0.6, 2.7, t, ha="center", fontsize=8.5, color=C["text"])
    save(fig, "25-7gun-plan.png")

# 26 Case study schematic
def fig_case():
    rng = np.random.default_rng(12)
    t = np.arange(100)
    price = 100 + np.concatenate([np.linspace(0,-8,30), np.linspace(-8,-10,20), np.linspace(-10,12,50)]) + rng.normal(0,0.5,100)
    m,s,h = macd_parts(price)
    fig, axes = plt.subplots(2,1,figsize=(10,6.8), sharex=True, gridspec_kw={"height_ratios":[1.25,1]})
    axes[0].plot(t, price, C["price"], lw=1.8); axes[0].set_title("Vaka Şeması — Düşüş, Uyumsuzluk, Boğa Kesişimi, Trend")
    # annotate zones
    axes[0].axvspan(0,40, color=C["bear"], alpha=0.08); axes[0].axvspan(40,60, color=C["accent"], alpha=0.1); axes[0].axvspan(60,99, color=C["bull"], alpha=0.08)
    axes[0].text(15, price.max(), "1. Düşüş", color=C["bear"]); axes[0].text(45, price.max(), "2. Uyarı", color=C["accent"]); axes[0].text(75, price.max(), "3. Trend", color=C["bull"])
    axes[1].plot(t,m,C["macd"],lw=2); axes[1].plot(t,s,C["signal"],lw=1.6); axes[1].axhline(0,color=C["zero"],ls="--")
    axes[1].bar(t,h,color=[C["hist_pos"] if x>=0 else C["hist_neg"] for x in h], alpha=0.35)
    for ax in axes: ax.grid(True, alpha=0.3)
    fig.tight_layout(); save(fig, "26-vaka-semasi.png")

# 27 Psychology meter
def fig_psych():
    fig, ax = plt.subplots(figsize=(10,4.2)); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0,4)
    ax.set_title("Duygu Metronomu — MACD ile Değil, Kuralla İşlem", fontsize=13)
    ax.add_patch(FancyBboxPatch((0.5,1.2), 9, 1.6, boxstyle="round,pad=0.04,rounding_size=0.2", facecolor="#1a303c", edgecolor=C["grid"], lw=1.5))
    ax.plot([1,9],[2,2], color=C["muted"], lw=4, solid_capstyle="round")
    for x,lab,col in [(1.5,"FOMO",C["bear"]),(3.5,"Acele",C["signal"]),(5,"Nötr plan",C["macd"]),(6.5,"Sabır",C["accent"]),(8.5,"Aşırı\nçekingen",C["bear"])]:
        ax.plot(x,2,"o",color=col,ms=14); ax.text(x, 0.6, lab, ha="center", color=col, fontsize=10)
    ax.annotate("İdeal bölge", xy=(5,2), xytext=(5,3.3), ha="center", color=C["macd"], arrowprops=dict(arrowstyle="->", color=C["macd"]))
    save(fig, "27-psikoloji.png")

# 28 Myths
def fig_myths():
    fig, ax = plt.subplots(figsize=(10,5.5)); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0,6)
    ax.set_title("MACD Mitleri vs Gerçekler", fontsize=14)
    rows = [
        ("Mit: Her kesişim kârdır", "Gerçek: Range'de çoğu kesişim gürültüdür"),
        ("Mit: MACD geleceği bilir", "Gerçek: Gecikmeli bir ölçüm aracıdır"),
        ("Mit: En iyi ayar gizlidir", "Gerçek: Sabit + disiplin > sihirli ayar"),
        ("Mit: Uyumsuzluk = kesin dönüş", "Gerçek: Uyarıdır; teyit ister"),
        ("Mit: Tek gösterge yeter", "Gerçek: Fiyat yapısı her zaman birincildir"),
    ]
    for i,(a,b) in enumerate(rows):
        y = 5.1 - i*0.95
        ax.add_patch(FancyBboxPatch((0.4,y-0.3), 4.4, 0.75, boxstyle="round,pad=0.02,rounding_size=0.1", facecolor="#2a1f1c", edgecolor=C["bear"], lw=1.2))
        ax.add_patch(FancyBboxPatch((5.2,y-0.3), 4.4, 0.75, boxstyle="round,pad=0.02,rounding_size=0.1", facecolor="#1c2a28", edgecolor=C["bull"], lw=1.2))
        ax.text(0.6, y+0.05, a, color=C["bear"], fontsize=10)
        ax.text(5.4, y+0.05, b, color=C["bull"], fontsize=10)
    save(fig, "28-mitler.png")

# 29 Journal template
def fig_journal():
    fig, ax = plt.subplots(figsize=(10,6)); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0,7)
    ax.set_title("MACD İşlem Günlüğü Şablonu", fontsize=14)
    fields = ["Tarih / sembol / zaman dilimi","Rejim (trend/range) + üst TF bias","Sinyal türü (kesişim/sıfır/hist/uyumsuzluk)",
              "Teyitler (seviye, hacim, RSI...)","Giriş / stop / hedefler (R)","Sonuç (R) + ekran görüntüsü notu","Hata / iyi karar / yarın kuralı"]
    for i,f in enumerate(fields):
        y = 5.8 - i*0.75
        ax.add_patch(FancyBboxPatch((0.6,y-0.25), 8.8, 0.6, boxstyle="round,pad=0.02,rounding_size=0.1",
                                    facecolor="#1a303c", edgecolor=C["grid"], lw=1))
        ax.text(0.9, y, f"□  {f}", va="center", fontsize=12)
    save(fig, "29-gunluk-sablon.png")

# 30 Roadmap poster end
def fig_endmap():
    fig, ax = plt.subplots(figsize=(10,5)); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0,5)
    ax.set_title("Kitaptan Sonraki 30 Gün", fontsize=14)
    boxes = [(0.4, "Gün 1–10", "Her gün 3 grafik\nişaretle, işlem açma"), (3.5, "Gün 11–20", "Kâğıt üzeri\niskelet A/B dene"), (6.6, "Gün 21–30", "Küçük riskle\nteklif + günlük")]
    for x,t,b in boxes:
        ax.add_patch(FancyBboxPatch((x,1.2), 2.8, 2.8, boxstyle="round,pad=0.05,rounding_size=0.2", facecolor="#1a303c", edgecolor=C["macd"], lw=2))
        ax.text(x+1.4, 3.4, t, ha="center", fontsize=13, fontweight="bold", color=C["accent"])
        ax.text(x+1.4, 2.2, b, ha="center", fontsize=11, color=C["text"])
    save(fig, "30-30gun-plan.png")

if __name__ == "__main__":
    fig_sma_ema(); fig_regimes(); fig_hidden_bull(); fig_hidden_bear()
    fig_settings(); fig_risk(); fig_checklist(); fig_mtf()
    fig_false(); fig_impulse(); fig_path(); fig_hist_phases()
    fig_macd_rsi(); fig_week(); fig_case(); fig_psych()
    fig_myths(); fig_journal(); fig_endmap()
    print("extra diagrams done")
