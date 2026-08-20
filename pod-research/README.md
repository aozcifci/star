# POD araştırması (Redbubble, TeePublic, Etsy)

Üç pazaryerinde satılan print-on-demand ürünleri, nişleri ve stilleri toplar;
**10 ürün önerisi** ve ChatGPT Images için **10 prompt** üretir
(orijinal sarkastik yazı, şeffaf PNG).

İki ritim:

1. **Günlük brifing** — bugün ne satılıyor.
2. **+40 gün ufku** — ABD takviminde 40 gün sonraki alışveriş gününe (ör. 4 Temmuz gibi) bakıp, o gün alınan ürünlere yakın tasarımlar.

## Teslimler

### Günlük (20 Ağustos 2026)

- [20 Ağustos 2026 brifing](reports/2026-08-20.md)
- [10 ChatGPT Images promptu](prompts/2026-08-20.md)
- [Canlı Google Suggest](reports/2026-08-20-autocomplete.md)

### +40 gün ufku (hedef: 29 Eylül 2026)

Bugün 20 Ağustos. 40 gün sonrası **29 Eylül 2026** = ABD’de Halloween alışveriş zirve haftası (Halloween 31 Ekim Cumartesi).

Karışım: **4 papercraft** · **3 önceden satılan tarz** · **3 yeni öneri**.

- [29 Eylül 2026 ufuk brifingi](reports/2026-09-29.md)
- [10 ChatGPT Images promptu](prompts/2026-09-29.md)
- [Canlı Google Suggest](reports/2026-09-29-autocomplete.md)

## Script

```bash
python3 pod-research/scripts/daily_research.py
python3 pod-research/scripts/daily_research.py --date 2026-09-29
```

Çıktılar:

- `data/YYYY-MM-DD.json` — ham öneriler
- `reports/YYYY-MM-DD-autocomplete.md` — otomatik özet

Redbubble, TeePublic ve Etsy vitrinleri bot koruması yüzünden scriptten
doğrudan çekilemez. Brifingde yayınlanmış trend raporları, canlı arama
önerileri ve pazaryeri sinyalleri birleştirilir.

## Tekrar çalıştırma

Örnek prompt:

> `pod-research` klasöründeki +40 gün yöntemini kullan. Bugünden 40 gün
> sonraki ABD pazarı alışveriş gününü bul (4 Temmuz örneği gibi). O güne
> yönelik alınan POD ürünlere yakın 10 prompt yaz: 4 papercraft, 3 önceden
> satılan tarza göre, 3 senin önerin. Scripti çalıştır.
> `reports/` brifingini Türkçe yaz. Promptlar İngilizce, şeffaf PNG,
> orijinal sarkastik yazı görselin içinde. Viral slogan kopyalama.
> Commit et, push et, PR'ı güncelle.

Telif / marka: Disney, FIFA, NFL, takım formaları, grup logoları,
karakter isimleri ve resmi farkındalık logoları (ör. pembe kurdele)
arama hacmi yüksek olsa da çoğu POD hesabı için yasaktır.
Raporda bunları **lisans riski** olarak işaretleriz.
