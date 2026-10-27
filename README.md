# Global Socio-Geographical Data Pipeline

Bu proje, dünyadaki tüm ülkelerin sosyo-coğrafi verilerini REST Countries API üzerinden toplayan, temizleyen, istatistiksel analizlerini gerçekleştiren, görselleştiren ve nihai bir özet rapor oluşturan uçtan uca (end-to-end) bir veri analitiği hattıdır.

---

## 🚀 Temel Özellikler

- **Veri Toplama:** Sayfalama (pagination) desteğiyle REST Countries API'den 254 ülkenin verisinin çekilmesi.
- **ETL & Temizleme:** Ham JSON yapısının düzleştirilmesi, dillerin ayrıştırılması ve tip dönüşümleri.
- **İstatistiksel Analiz:**
  - Yüzölçümü ve nüfus arasındaki Pearson korelasyon analizi.
  - Kilometrekare başına düşen nüfus yoğunluğu dağılımları ve ekstremumlar (en yoğun / en seyrek).
  - Kıtalara göre en yaygın resmi / konuşulan dillerin frekans analizi.
- **Keşifsel Veri Görselleştirmesi:** Seaborn ve Matplotlib ile logaritmik saçılım, histogram ve çubuk grafikleri.
- **Orkestrasyon:** Tek komutla (`python main.py`) tüm hattın sıralı ve hatasız çalıştırılması.

---

## 📁 Proje Yapısı

```text
data_project/
│
├── .env.example                # Örnek ortam değişkenleri şablonu
├── .gitignore                  # Git hariç tutma kuralları (API anahtarı ve ham veriler korunur)
├── requirements.txt            # Python kütüphane bağımlılıkları
├── main.py                     # Tüm pipeline'ı yöneten orkestratör
│
├── get_countries.py            # API veri çekme modülü
├── process_data.py             # ETL ve veri temizleme modülü
├── analyze_correlation.py      # Nüfus & yüzölçümü korelasyon analizi
├── analyze_density.py          # Nüfus yoğunluğu analizi
├── analyze_languages.py        # Kıtasal dil dağılım analizi
├── visualize_data.py           # Grafik ve görselleştirme üretimi
├── generate_report.py          # Nihai Markdown raporu derleyicisi
│
├── data/
│   ├── raw/                    # API'den gelen ham JSON verisi (git tarafından yok sayılır)
│   └── processed/              # Temizlenmiş ve analiz edilmiş CSV çıktıları
│
└── reports/
    ├── final_report.md         # Nihai analiz raporu
    └── figures/                # Üretilen görsel grafikler (*.png)
```

---

## 🛠️ Kurulum

### 1. Bağımlılıkların Yüklenmesi
```bash
pip install -r requirements.txt
```

### 2. Ortam Değişkenlerinin Ayarlanması
`.env.example` dosyasını kopyalayarak `.env` oluşturun ve API anahtarınızı girin:
```bash
# Windows PowerShell
Copy-Item .env.example .env
```
`.env` dosyasını açıp token bilginizi ekleyin:
```env
REST_COUNTRIES_API_TOKEN=your_token_here
```

---

## ▶️ Kullanım

### Pipeline'ı Çalıştırma:
Tüm adımları (veri işleme, analizler, görselleştirme ve raporlama) tek bir komutla başlatabilirsiniz:
```bash
python main.py
```

### Parametreler:
- `python main.py --fetch` : API'den en güncel ham veriyi zorla yeniden çeker ve hattı baştan çalıştırır.
- `python main.py --skip-fetch` : API çağrısını doğrudan atlar ve mevcut yerel veriyi kullanır.

---

## 📊 Çıktılar

- **Veriler:** `data/processed/countries_processed.csv` ve özet tablolar.
- **Grafikler:** `reports/figures/` altında PNG formatında yüksek çözünürlüklü grafikler.
- **Rapor:** `reports/final_report.md` dosyasında detaylı sonuç metni.
