# Günlük POD araştırması (Redbubble, TeePublic, Etsy)

Her gün üç pazaryerinde satılan print-on-demand ürünleri, nişleri ve stilleri
toplar; **3 ürün önerisi** ve ChatGPT Images için **3 prompt** üretir.

## Bugünün teslimi

- [20 Ağustos 2026 brifing](reports/2026-08-20.md)
- [Canlı Google Suggest dökümü](reports/2026-08-20-autocomplete.md)

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
> 3 adet tasarım/ürün önerisi, ChatGPT Images için 3 prompt (1 papercraft,
> 1 o günün en çok tercih edilen tarzı, 1 senin önerdiğin tarz).
> Commit et, push et, PR'ı güncelle.

Telif / marka: Disney, FIFA, NFL, takım formaları, grup logoları ve
karakter isimleri arama hacmi yüksek olsa da çoğu POD hesabı için yasaktır.
Raporda bunları **lisans riski** olarak işaretleriz.
