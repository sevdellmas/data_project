import json
import os
from pathlib import Path
from dotenv import load_dotenv
import requests

# Ortam değişkenlerini .env dosyasından yükle
load_dotenv()


def fetch_countries(output_path: Path = Path("data/raw/countries.json")):
    """
    REST Countries v5 API'sinden tüm ülkeleri sayfalanarak (pagination) çeker
    ve raw JSON olarak hedeflenen yola kaydeder.
    """
    token = os.getenv("REST_COUNTRIES_API_TOKEN")
    if not token:
        raise ValueError(
            "REST_COUNTRIES_API_TOKEN bulunamadı! Lütfen .env dosyanızı veya ortam değişkeninizi kontrol edin."
        )

    url = "https://api.restcountries.com/countries/v5"
    headers = {"Authorization": f"Bearer {token}"}

    all_countries = []
    limit = 100  # API'nin tek seferde izin verdiği üst sınır
    offset = 0

    print("API'den tüm ülkeler sayfalanarak (pagination) alınıyor...")

    while True:
        params = {"limit": limit, "offset": offset}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            response_json = response.json()
        except Exception as e:
            print(f"İstek sırasında hata oluştu: {e}")
            break

        data_section = response_json.get("data", {})

        if isinstance(data_section, dict):
            objects = data_section.get("objects", [])
            if isinstance(objects, list):
                all_countries.extend(objects)

            meta = data_section.get("meta", {})
            total = meta.get("total", "?")
            more = meta.get("more", False)
            print(f"Alındı: {len(all_countries)} / {total} ülke (offset={offset}, limit={limit})")

            if not more or not objects:
                break
            offset += len(objects)

        elif isinstance(data_section, list):
            all_countries.extend(data_section)
            break
        else:
            break

    print(f"\nToplam çekilen ülke sayısı: {len(all_countries)}")

    full_envelope = {
        "success": True,
        "data": {
            "objects": all_countries,
            "meta": {
                "total": len(all_countries),
                "count": len(all_countries),
                "limit": len(all_countries),
                "offset": 0,
                "more": False
            }
        },
        "errors": []
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(full_envelope, f, ensure_ascii=False, indent=2)

    print(f"Tüm veriler başarıyla kaydedildi: {output_path}")
    return all_countries


if __name__ == "__main__":
    fetch_countries()
