import json
from pathlib import Path
import pandas as pd


def extract_languages(lang_data):
    """
    Diller alanını (dict, list veya str) temiz ve virgülle ayrılmış bir metne dönüştürür.
    Örn: ["English", "Spanish"] veya {"eng": "English", "spa": "Spanish"} -> "English, Spanish"
    """
    if not lang_data:
        return None

    if isinstance(lang_data, list):
        names = []
        for item in lang_data:
            if isinstance(item, dict):
                names.append(item.get("name") or item.get("common") or str(item))
            elif isinstance(item, str):
                names.append(item)
        return ", ".join(filter(None, names)) if names else None

    elif isinstance(lang_data, dict):
        names = []
        for val in lang_data.values():
            if isinstance(val, dict):
                names.append(val.get("name") or val.get("common") or str(val))
            elif isinstance(val, str):
                names.append(val)
        return ", ".join(filter(None, names)) if names else None

    elif isinstance(lang_data, str):
        return lang_data

    return None


def load_raw_data(file_path: Path):
    """
    data/raw/countries.json dosyasını 'success', 'data' ve 'errors'
    envelope (zarf) yapısını dikkate alarak güvenli bir şekilde okur ve
    ülke listesini döndürür.
    """
    print(f"Lokal dosya (`{file_path}`) okunuyor...")
    if not file_path.exists():
        raise FileNotFoundError(f"Hata: {file_path} dosyası bulunamadı!")

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            raw_json = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON formatı bozuk: {e}")

    raw_data = None
    if isinstance(raw_json, dict):
        # 'success' ve 'errors' alanları kontrolü
        if "success" in raw_json and not raw_json["success"]:
            print("Bilgi: JSON zarfında 'success' değeri False olarak işaretlenmiş.")

        if raw_json.get("errors"):
            print(f"Bilgi / Hata detayları: {raw_json.get('errors')}")

        # Asıl ülke verisi 'data' anahtarında yer alır
        if "data" in raw_json:
            raw_data = raw_json["data"]
        else:
            raw_data = raw_json
    else:
        raw_data = raw_json

    if not raw_data:
        print("Uyarı: 'data' anahtarı boş veya geçerli bir veri içermiyor.")
        return []

    # 'data' doğrudan bir liste, 'objects' içeren bir sözlük veya anahtar-değer sözlüğü olabilir
    countries_list = []
    if isinstance(raw_data, dict) and "objects" in raw_data and isinstance(raw_data["objects"], list):
        countries_list = raw_data["objects"]
    elif isinstance(raw_data, list):
        for item in raw_data:
            if isinstance(item, list):
                countries_list.extend(item)
            elif isinstance(item, dict):
                countries_list.append(item)
    elif isinstance(raw_data, dict):
        for k, v in raw_data.items():
            if k == "meta":
                continue
            if isinstance(v, list):
                countries_list.extend(v)
            elif isinstance(v, dict):
                countries_list.append(v)

    # Yalnızca geçerli sözlük (dict) olan ülke kayıtlarını filtrele
    valid_countries = [c for c in countries_list if isinstance(c, dict)]
    print(f"Yüklenen geçerli ham ülke kayıt sayısı: {len(valid_countries)}")
    return valid_countries


def process_countries_data(countries_list):
    """
    Ham ülke listesini pandas ile düzleştirir, seçili alanları temizler ve DataFrame döndürür.
    """
    expected_columns = [
        "Country",
        "Official_Name",
        "Population",
        "Area",
        "Alpha2_Code",
        "Region",
        "Languages"
    ]

    if not countries_list:
        return pd.DataFrame(columns=expected_columns)

    # 1. Dilleri ham veriden güvenle çıkar
    cleaned_languages = [extract_languages(c.get("languages")) for c in countries_list]

    # 2. pandas ile iç içe alanları düzleştir (normalize)
    df = pd.json_normalize(countries_list)

    df_clean = pd.DataFrame()

    # Ülke Adı (name.common veya names.common)
    country_col = None
    for col in ["name.common", "names.common", "name", "common_name"]:
        if col in df.columns:
            country_col = col
            break
    df_clean["Country"] = df[country_col] if country_col else None

    # Resmi Ülke Adı (name.official veya names.official)
    official_col = None
    for col in ["name.official", "names.official", "official_name"]:
        if col in df.columns:
            official_col = col
            break
    df_clean["Official_Name"] = df[official_col] if official_col else None

    # Nüfus (population)
    if "population" in df.columns:
        df_clean["Population"] = pd.to_numeric(df["population"], errors="coerce")
    else:
        df_clean["Population"] = None

    # Yüzölçümü (area.kilometers veya area)
    if "area.kilometers" in df.columns:
        df_clean["Area"] = pd.to_numeric(df["area.kilometers"], errors="coerce")
    elif "area" in df.columns:
        df_clean["Area"] = df["area"].apply(
            lambda x: x.get("kilometers") if isinstance(x, dict) else pd.to_numeric(x, errors="coerce")
        )
    else:
        df_clean["Area"] = None

    # İki Harfli Ülke Kodu (codes.alpha_2 veya cca2)
    code_col = None
    for col in ["codes.alpha_2", "cca2", "codes.alpha2", "alpha2Code"]:
        if col in df.columns:
            code_col = col
            break
    df_clean["Alpha2_Code"] = df[code_col] if code_col else None

    # Bölge (region veya regions.geo.un)
    region_col = None
    for col in ["region", "regions.geo.un"]:
        if col in df.columns:
            region_col = col
            break

    if region_col:
        df_clean["Region"] = df[region_col].apply(
            lambda x: x[0] if isinstance(x, list) and len(x) > 0 else (x.get("name") if isinstance(x, dict) else x)
        )
    else:
        df_clean["Region"] = None

    # Diller (languages)
    if any(cleaned_languages):
        df_clean["Languages"] = cleaned_languages
    elif "languages" in df.columns:
        df_clean["Languages"] = df["languages"].apply(extract_languages)
    else:
        df_clean["Languages"] = None

    # Eksik ülke isimlerini temizle
    df_clean = df_clean.dropna(subset=["Country"])
    df_clean = df_clean[df_clean["Country"].astype(str).str.strip() != ""]

    return df_clean


def main(raw_file: Path = Path("data/raw/countries.json"), output_file: Path = Path("data/processed/countries_processed.csv")):
    raw_file = Path(raw_file)
    output_file = Path(output_file)
    output_dir = output_file.parent

    # 1. Ham veriyi yükle
    countries = load_raw_data(raw_file)

    # 2. Veriyi işle ve temizle
    df_clean = process_countries_data(countries)

    # 3. Sonuçları CSV olarak kaydet
    output_dir.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"\nİşlem tamamlandı! Kayıt yeri: {output_file}")
    print(f"Toplam işlenen ülke sayısı: {len(df_clean)}")
    if not df_clean.empty:
        print("\nOluşan tablonun ilk 3 satırı:")
        print(df_clean.head(3))

    return df_clean


if __name__ == "__main__":
    main()
