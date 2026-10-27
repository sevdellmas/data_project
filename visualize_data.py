from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def generate_visualizations(
    processed_dir: Path = Path("data/processed"),
    figures_dir: Path = Path("reports/figures")
):
    # Görsel stilini ayarlayalım
    sns.set_theme(style="whitegrid")
    plt.rcParams["font.sans-serif"] = "Segoe UI"

    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)
    processed_dir = Path(processed_dir)

    # 1. Verileri Okuma
    df_clean = pd.read_csv(processed_dir / "countries_processed.csv")
    df_corr = df_clean.dropna(subset=["Population", "Area"]).copy()
    df_corr = df_corr[(df_corr["Area"] > 0) & (df_corr["Population"] > 0)]

    # --- GRAFİK 1: Scatter Plot (Alan vs Nüfus İlişkisi) ---
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df_corr,
        x="Area",
        y="Population",
        hue="Region",
        palette="deep",
        alpha=0.7,
        s=60,
    )
    plt.title(
        "Yüzölçümü (Area) ile Nüfus (Population) İlişkisi",
        fontsize=14,
        fontweight="bold",
    )
    plt.xlabel("Yüzölçüm (km²)", fontsize=11)
    plt.ylabel("Nüfus", fontsize=11)
    plt.xscale("log")  # Geniş aralığı logaritmik ölçekle dengeliyoruz
    plt.yscale("log")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    scatter_path = figures_dir / "area_vs_population_scatter.png"
    plt.savefig(scatter_path, dpi=300)
    plt.close()

    # --- GRAFİK 2: Histogram (Nüfus Yoğunluğu Dağılımı) ---
    df_corr["Density"] = df_corr["Population"] / df_corr["Area"]
    plt.figure(figsize=(10, 6))
    sns.histplot(
        df_corr["Density"],
        bins=50,
        kde=True,
        color="skyblue",
        log_scale=True,  # Yoğunluk dağılımındaki uç değerler için log ölçek
    )
    plt.title(
        "Nüfus Yoğunluğu Dağılımı (Logaritmik Ölçek)",
        fontsize=14,
        fontweight="bold",
    )
    plt.xlabel("Nüfus Yoğunluğu (Kişi/km² - Log)", fontsize=11)
    plt.ylabel("Ülke Sayısı", fontsize=11)
    plt.tight_layout()
    hist_path = figures_dir / "population_density_hist.png"
    plt.savefig(hist_path, dpi=300)
    plt.close()

    # --- GRAFİK 3: Bar Chart (Kıtalara Göre En Yaygın Diller) ---
    lang_summary_path = processed_dir / "continent_languages_summary.csv"
    bar_path = None
    if lang_summary_path.exists():
        df_lang = pd.read_csv(lang_summary_path)

        plt.figure(figsize=(12, 7))
        sns.barplot(
            data=df_lang,
            x="Country_Count",
            y="Languages_List",
            hue="Region",
            dodge=False,
            palette="muted",
        )
        plt.title(
            "Kıtalara Göre En Yaygın Diller ve Ülke Sayıları",
            fontsize=14,
            fontweight="bold",
        )
        plt.xlabel("Konuşulan Ülke Sayısı", fontsize=11)
        plt.ylabel("Dil", fontsize=11)
        plt.legend(title="Kıta", bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()
        bar_path = figures_dir / "continent_languages_bar.png"
        plt.savefig(bar_path, dpi=300)
        plt.close()

    print(
        "Tüm keşifsel analiz grafikleri başarıyla oluşturuldu ve"
        f" '{figures_dir}' klasörüne kaydedildi!"
    )
    return scatter_path, hist_path, bar_path


if __name__ == "__main__":
    generate_visualizations()
