# T-shirt kelime araştırması

Her gün Amazon, eBay, Redbubble, TeePublic ve Pinterest t-shirt kategorisinde
aranan kelimeleri toplayıp `reports/` altına yazmak için.

## Bugünün raporu

- [16 Ağustos 2026 günlük brifing](reports/2026-08-16.md)

## Scripti çalıştırma

Canlı autocomplete (Amazon + eBay + Google) çekimi:

```bash
python3 tshirt-keyword-research/scripts/daily_research.py
```

Çıktılar:

- `data/YYYY-MM-DD.json` — ham öneriler
- `reports/YYYY-MM-DD-autocomplete.md` — otomatik özet

Redbubble, TeePublic ve Pinterest bot koruması yüzünden scriptten doğrudan
çekilemez. Günlük brifingde bu üç platform için yayınlanmış trend raporları,
niş izleyicileri ve arama önerileri birleştirilir.

## Her gün otomatik almak için

Bu agent tek seferlik çalışır. Günlük teslimat için Cursor'da **Automation**
kurun: her gün aynı prompt ile Cloud Agent'ı çalıştırın.

Örnek prompt:

> `tshirt-keyword-research` klasöründeki yöntemi kullan. Amazon, eBay,
> Redbubble, TeePublic ve Pinterest t-shirt kategorisinde bugün aranan
> kelimeleri araştırman. Scripti çalıştır, `reports/YYYY-MM-DD.md` brifingini
> Türkçe yaz, commit et ve PR'ı güncelle.

Telif / marka: Disney, NFL, FIFA, takım formaları ve grup logoları arama
hacmi yüksek olsa da çoğu POD hesabı için yasaktır. Raporda bunları
**lisans riski** olarak işaretleriz.
