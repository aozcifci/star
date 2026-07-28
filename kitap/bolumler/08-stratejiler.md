# Bölüm 8 — Stratejiler ve Karar Akışı

Bu bölüm “sinyali işleme çevirme” katmanıdır. Amaç ezber strateji değil; **tekrar edilebilir karar süreci** kurmaktır.

## 8.1 Temel karar akışı

![Karar akışı](../gorseller/13-karar-akisi.png)

1. Üst TF trend / bias  
2. MACD sinyali (kesişim, sıfır, ıraksama, histogram)  
3. Fiyat yapısı / mum onayı  
4. Risk: stop, hedef, pozisyon boyutu  
5. Yönetim: histogram zayıflayınca veya yapı bozulunca çık  

## 8.2 Strateji A — Trend yönünde sinyal kesişimi

**Mantık:** Trend varken momentum dönüşlerini yakalamak.

Kurallar (örnek):

- D1 MACD > 0 (bullish bias)
- H4’te MACD, sinyali yukarı keser
- Fiyat destek / yükselen yapıda
- Stop: son swing low altı
- Hedef: 1.5R–2R veya bir sonraki direnç
- Çıkış ek kuralı: histogram peş peşe küçülüp bearish kesişim gelirse

## 8.3 Strateji B — Sıfır çizgisi dönüşü

**Mantık:** Kısa/uzun EMA’nın yer değiştirmesini trend değişimi kabul etmek.

Kurallar:

- MACD sıfırın altına/üstüne net kapanışla geçer
- Hacim / kırılım mumları teyit eder
- Erken kesişimle değil, sıfır geçişi + retest ile girilir (daha geç, daha seçici)

## 8.4 Strateji C — Regular ıraksama + teyit

**Mantık:** Momentum zayıflamasını dönüşe çevirmek.

Kurallar:

- İki net swing ile regular ıraksama
- MACD aşırı bölgede
- Teyit: sinyal kesişimi veya reversal mum
- Trende karşı olduğu için daha küçük pozisyon / daha sıkı risk

## 8.5 Strateji D — Hidden ıraksama ile trend devamı

**Mantık:** Trend içi pullback’te devam aramak.

Kurallar:

- Ana trend net (ör. HH-HL yükseliş)
- Gizli bullish ıraksama
- Pullback sonlanırken bullish kesişim
- Stop pullback dibinin altı

## 8.6 Ne zaman işlem yok?

- Yatay, sıkı bant (whipsaw bölgesi)
- Önemli haber öncesi
- Üst TF ile alt TF tamamen çelişiyorsa
- Risk/ödül < 1
- Zaten aşırı uzamış hareketin ortasında “geç tren”

Whipsaw örneği:

![Whipsaw](../gorseller/11-whipsaw-yanlis-sinyal.png)

Yatay piyasada MACD sürekli kesişim üretir. Bu, strateji değil gürültüdür.

## Bu bölümün özeti

Strateji = sinyal + bağlam + risk.  
En iyi MACD stratejisi, “her kesişimi almak” değil; “doğru ortamda seçmek”tir.
