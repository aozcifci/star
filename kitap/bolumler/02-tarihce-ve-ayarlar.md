# Bölüm 2 — Tarihçe ve Standart Ayarlar

## Kim buldu?

MACD’yi **Gerald Appel** 1970’lerin sonlarında (genelde 1977 olarak anılır) geliştirdi. Amaç, fiyatın kısa ve uzun vadeli üstel ortalamaları arasındaki ilişkiyi tek bir momentum göstergesine indirmekti.

## Histogram kim ekledi?

Orijinal MACD’de asıl vurgu MACD ve sinyal çizgisindeydi. **Thomas Aspray** 1986’da **histogramı** popülerleştirerek kesişimlerin görsel olarak daha erken fark edilmesini sağladı. Bugün neredeyse tüm platformlarda histogram varsayılandır.

## Neden 12, 26, 9?

Standart ayar:

| Parametre | Değer | Anlamı |
|-----------|------:|--------|
| Hızlı EMA | 12 | Kısa vadeli ortalama |
| Yavaş EMA | 26 | Uzun vadeli ortalama |
| Sinyal EMA | 9 | MACD’nin tetik ortalaması |

Bu sayılar tarihsel olarak **günlük grafik** ve eski piyasa takvimine (haftalık işlem günleri) göre kalibre edilmiştir. Bugün “kutsal” değildir; ama **en çok kullanılan**, en çok test edilen ve en çok izlenen varsayılandır.

Bu yüzden:

- Yeni başlayanlar için varsayılan **12-26-9** ile başlamak doğru tercihtir.
- Herkese özel “sihirli ayar” aramak çoğu zaman overfitting (aşırı uyum) üretir.

## MACD lagging midir, leading midir?

Temelde **lagging**’dir çünkü hareketli ortalamalardan türetilir.  
Ancak:

- Histogramın daralması / yön değiştirmesi
- Iraksama (divergence)

gibi unsurlar, fiyat dönüşünden *önce* uyarı verebilir. Bu yüzden pratikte “gecikmeli çekirdek + erken uyarı katmanları” diye düşünmek daha doğrudur.

## Platformlarda nasıl eklenir?

Hemen her grafik platformunda `MACD` olarak bulunur. Varsayılan genelde `(12, 26, 9)` gelir. Kaynak veri olarak çoğu zaman **kapanış fiyatı** kullanılır.

## Bu bölümün özeti

Appel → MACD; Aspray → histogram.  
Standart ayar 12-26-9’dur.  
Varsayılanla ustalaşmadan ayar karıştırmayın.
