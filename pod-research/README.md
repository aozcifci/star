# Günlük POD araştırması (Redbubble, TeePublic, Etsy)

Her gün üç pazaryerinde satılan print-on-demand ürünleri, nişleri ve stilleri
toplar; **10 ürün önerisi** ve ChatGPT Images için **10 prompt** üretir
(farklı tarzlar, orijinal sarkastik yazı, şeffaf PNG).

## Bugünün teslimi

- [29 Ağustos 2026 brifing](reports/2026-08-29.md)
- [10 ChatGPT Images promptu](prompts/2026-08-29.md)
- [Canlı Google Suggest dökümü](reports/2026-08-29-autocomplete.md)

Önceki günler: [28 Ağustos](reports/2026-08-28.md) · [27 Ağustos](reports/2026-08-27.md) · [26 Ağustos](reports/2026-08-26.md) · [25 Ağustos](reports/2026-08-25.md) · [24 Ağustos](reports/2026-08-24.md) · [23 Ağustos](reports/2026-08-23.md) · [22 Ağustos](reports/2026-08-22.md) · [21 Ağustos](reports/2026-08-21.md) · [20 Ağustos](reports/2026-08-20.md)

## Script

```bash
python3 pod-research/scripts/daily_research.py
```

Çıktılar:

- `data/YYYY-MM-DD.json` — ham öneriler
- `reports/YYYY-MM-DD-autocomplete.md` — otomatik özet

Redbubble, TeePublic ve Etsy vitrinleri bot koruması yüzünden scriptten
doğrudan çekilemez. Günlük brifingde yayınlanmış trend raporları, canlı
arama önerileri ve pazaryeri sinyalleri birleştirilir.

## Her gün otomatik almak için

Bu agent tek seferlik çalışır. Günlük teslimat için aynı prompt ile
yeniden çalıştırın (Cursor Automation veya bu konuşmadaki günlük timer).

Örnek prompt:

> `pod-research` klasöründeki yöntemi kullan. Bugün Redbubble, TeePublic
> ve Etsy'de satılan print on demand ürünleri araştır. Scripti çalıştır.
> `reports/YYYY-MM-DD.md` brifingini Türkçe yaz: pazaryeri ürün özeti,
> araştırmadaki nişlere göre 10 adet tasarım/ürün önerisi, ChatGPT Images
> için 10 prompt (hepsi farklı tarz; papercraft, coquette ve analog
> risograph dahil; orijinal sarkastik yazı her görselde).
> Her prompt şeffaf arka plan / arka plansız PNG olmalı: sadece görsel,
> zemin, oda, gökyüzü, stüdyo, kâğıt yok. Viral sloganları kopyalama.
> Commit et, push et, PR'ı güncelle.

Telif / marka: Disney, FIFA, NFL, takım formaları, grup logoları ve
karakter isimleri arama hacmi yüksek olsa da çoğu POD hesabı için yasaktır.
Raporda bunları **lisans riski** olarak işaretleriz.
