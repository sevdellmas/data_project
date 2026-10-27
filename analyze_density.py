from pathlib import Path
import pandas as pd


def analyze_density(
    csv_path: Path = Path("data/processed/countries_processed.csv"),
    output_path: Path = Path("data/processed/population_density_summary.csv")
):
    # 1. Temiz veriyi oku
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)

    # 2. Nüfus yoğunluğunu hesapla (Population / Area)
    df_density = df.dropna(subset=["Population", "Area"]).copy()
    df_density = df_density[df_density["Area"] > 0]

    df_density["Population_Density"] = df_density["Population"] / df_density["Area"]

    # 3. Analizler: En yüksek ve en düşük nüfus yoğunluğuna sahip ülkeler
    top_dense = df_density.sort_values(by="Population_Density", ascending=False).head(10)
    lowest_dense = df_density.sort_values(by="Population_Density", ascending=True).head(10)

    # 4. Sonuçları CSV dosyası olarak kaydedelim
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_density.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Analiz tamamlandı! Tüm nüfus yoğunluğu verileri kaydedildi: {output_path}\n")
    print("=" * 50)
    print("DÜNYANIN EN YOĞUN NÜFUSLU 5 ÜLKESİ")
    print("=" * 50)
    for idx, row in top_dense.head(5).iterrows():
        print(
            f"  - {row['Country']} ({row['Region']}):"
            f" {row['Population_Density']:.2f} kişi/km²"
        )

    print("\n" + "=" * 50)
    print("DÜNYANIN EN SEYREK NÜFUSLU 5 ÜLKESİ")
    print("=" * 50)
    for idx, row in lowest_dense.head(5).iterrows():
        print(
            f"  - {row['Country']} ({row['Region']}):"
            f" {row['Population_Density']:.4f} kişi/km²"
        )

    return df_density, top_dense, lowest_dense


if __name__ == "__main__":
    analyze_density()
