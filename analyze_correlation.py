from pathlib import Path
import pandas as pd


def analyze_correlation(
    csv_path: Path = Path("data/processed/countries_processed.csv"),
    output_path: Path = Path("data/processed/area_population_correlation.csv")
):
    # 1. Temiz veriyi oku
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)

    # Eksik verileri temizle
    df_corr = df.dropna(subset=["Population", "Area"]).copy()
    df_corr = df_corr[(df_corr["Area"] > 0) & (df_corr["Population"] > 0)]

    # 2. Korelasyon katsayısını hesapla (Pearson)
    correlation = df_corr["Area"].corr(df_corr["Population"])

    # 3. En büyük yüzölçümüne sahip 10 ülke ve nüfusları
    largest_countries = df_corr.sort_values(by="Area", ascending=False).head(10)

    # Sonuçları kaydet
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    largest_countries.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("=" * 50)
    print("ALAN VE NÜFUS İLİŞKİSİ ANALİZİ")
    print("=" * 50)
    print(f"Yüzölçümü ile Nüfus arasındaki Pearson Korelasyonu: {correlation:.4f}")
    print(
        "(Not: Korelasyonun 0'a yakın olması, büyük yüzölçümünün otomatik olarak"
        " en kalabalık ülke olduğu anlamına gelmediğini gösterir.)\n"
    )

    print("En Büyük Yüzölçümüne Sahip 5 Ülke:")
    for idx, row in largest_countries.head(5).iterrows():
        print(
            f"  - {row['Country']} ({row['Region']}): Alan: {row['Area']:,.0f} km² |"
            f" Nüfus: {row['Population']:,}"
        )

    return correlation, largest_countries


if __name__ == "__main__":
    analyze_correlation()
