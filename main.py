"""
Main Pipeline Orchestrator
Bu script tüm veri analizi hattını (veri çekme, temizleme, analizler, görselleştirme ve raporlama)
sırasıyla ve tek komutla çalıştırır.
"""

import argparse
from pathlib import Path
import sys
import time

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from analyze_correlation import analyze_correlation
from analyze_density import analyze_density
from analyze_languages import analyze_languages
from generate_report import generate_report
from get_countries import fetch_countries
import process_data
from visualize_data import generate_visualizations


def print_step(step_number: int, title: str):
    print("\n" + "=" * 60)
    print(f"[{step_number}/5] {title.upper()}")
    print("=" * 60)


def run_pipeline(force_fetch: bool = False, skip_fetch: bool = False):
    start_time = time.time()
    raw_data_path = Path("data/raw/countries.json")

    print("\n>>> VERI ANALIZI VE RAPORLAMA HATTI BASLATILIYOR...\n")

    # 1. Adım: Veri Çekme (API)
    print_step(1, "Veri Toplama (Data Ingestion)")
    if skip_fetch:
        print("[>>] '--skip-fetch' bayragi verildi. API'den veri cekme adimi atlandi.")
    elif force_fetch or not raw_data_path.exists():
        if force_fetch:
            print("[*] '--fetch' bayragi aktif. API'den guncel veriler cekiliyor...")
        else:
            print(f"[i] {raw_data_path} bulunamadi. API'den veriler cekiliyor...")
        try:
            fetch_countries(output_path=raw_data_path)
        except Exception as e:
            print(f"[!] Veri cekme hatasi: {e}")
            sys.exit(1)
    else:
        print(f"[✓] Ham veri mevcut ({raw_data_path}). API istegi atlandi.")
        print("    (Yeniden cekmek icin: python main.py --fetch)")

    # 2. Adım: Veri İşleme & Temizleme (ETL)
    print_step(2, "Veri On Isleme ve Temizleme (ETL)")
    df_clean = process_data.main(raw_file=raw_data_path)

    # 3. Adım: Analizler
    print_step(3, "Istatistiksel Analizlerin Gerceklestirilmesi")
    print("-> Korelasyon analizi calistiriliyor...")
    analyze_correlation()

    print("\n-> Nufus yogunlugu analizi calistiriliyor...")
    analyze_density()

    print("\n-> Kitalara gore dil dagilimi analizi calistiriliyor...")
    analyze_languages()

    # 4. Adım: Keşifsel Görselleştirme
    print_step(4, "Gorsellestirmelerin Uretilmesi (Seaborn / Matplotlib)")
    generate_visualizations()

    # 5. Adım: Final Raporunun Derlenmesi
    print_step(5, "Nihai Markdown Raporunun Olusturulmasi")
    report_file = generate_report()

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"[✓] TUM PIPELINE BASARIYLA TAMAMLANDI! (Sure: {elapsed:.2f} sn)")
    print(f"[*] Nihai Rapor: {report_file}")
    print("[*] Uretilen Grafikler: reports/figures/")
    print("[*] Islenmis Veriler: data/processed/")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Global Socio-Geographical Data Pipeline Orchestrator"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--fetch",
        action="store_true",
        help="API'den en guncel veriyi yeniden cekmeyi zorunlu kilar.",
    )
    group.add_argument(
        "--skip-fetch",
        action="store_true",
        help="API'den veri cekme adimini dogrudan atlar.",
    )

    args = parser.parse_args()
    run_pipeline(force_fetch=args.fetch, skip_fetch=args.skip_fetch)
