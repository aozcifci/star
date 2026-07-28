# Ek B — Formül Kartı (Tek Sayfa)

## Standart ayar
`(fast, slow, signal) = (12, 26, 9)`

## Formüller
```
α(N)        = 2 / (N + 1)
EMA_t       = α * fiyat_t + (1 - α) * EMA_(t-1)
MACD        = EMA(12) - EMA(26)
Sinyal      = EMA(9) of MACD
Histogram   = MACD - Sinyal
```

## Hızlı yorum
```
MACD > 0          → bullish bias
MACD < 0          → bearish bias
MACD × sinyal ↑   → bullish tetik
MACD × sinyal ↓   → bearish tetik
Histogram ↑       → ivme artışı
Histogram ↓       → ivme kaybı
```

## Iraksama kısa tablo
```
Regular bullish : fiyat LL + MACD HL
Regular bearish : fiyat HH + MACD LH
Hidden bullish  : fiyat HL + MACD LL
Hidden bearish  : fiyat LH + MACD HH
```

## 5 saniyelik kural
Üst TF bias + MACD sinyali + mum onayı + stop/hedef yoksa → işlem yok.
