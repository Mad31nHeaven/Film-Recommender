import requests
import pycountry
def fetch_providers(tmdb_id,country_code):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/watch/providers"
    resp = requests.get(url, params={"api_key": ''}) #<<<YOUR API HERE, get it from TMDB.
    data = resp.json().get("results", {}).get(country_code, {})
    return {
      "flatrate": [p["provider_name"] for p in data.get("flatrate", [])],
      "buy":     [p["provider_name"] for p in data.get("buy", [])],
      "rent":    [p["provider_name"] for p in data.get("rent", [])],
    }
