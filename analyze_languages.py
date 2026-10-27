from pathlib import Path
import pandas as pd


def analyze_languages(
    csv_path: Path = Path("data/processed/countries_processed.csv"),
    output_path: Path = Path("data/processed/continent_languages_summary.csv")
):
    # 1. Temiz veriyi oku
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)

    # 2. Diller sütununu temizle ve satırlara ayır (Explode)
    df["Languages_List"] = (
        df["Languages"]
        .fillna("")
        .apply(lambda x: [lang.strip() for lang in str(x).split(",") if lang.strip()])
    )

    df_exploded = df.explode("Languages_List")
    df_exploded = df_exploded[df_exploded["Languages_List"] != ""]

    # 3. Kıta (Region) ve Dile göre gruplayıp sayalım
    language_counts = (
        df_exploded.groupby(["Region", "Languages_List"])
        .size()
        .reset_index(name="Country_Count")
    )

    # Her kıta için en yaygın dilleri sıralayalım ve ilk 5'i güvenli şekilde alalım
    top_languages_per_region = (
        language_counts.sort_values(by=["Region", "Country_Count"], ascending=[True, False])
        .groupby("Region")
        .head(5)
        .reset_index(drop=True)
    )

    # 4. Sonuçları CSV dosyası olarak kaydedelim
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    top_languages_per_region.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Analiz tamamlandı! Sonuçlar kaydedildi: {output_path}\n")
    print("=" * 50)
    print("KITALARA GÖRE EN YAYGIN DİLLER ÖZETİ")
    print("=" * 50)

    # 5. Terminalde okunaklı bir şekilde yazdıralım
    for region, group in top_languages_per_region.groupby("Region"):
        print(f"\n[{region} Kıtası]")
        for idx, row in group.iterrows():
            print(f"  - {row['Languages_List']}: {row['Country_Count']} ülke")

    return top_languages_per_region


if __name__ == "__main__":
    analyze_languages()
