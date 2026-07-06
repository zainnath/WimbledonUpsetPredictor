import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "tennis-api-atp-wta-itf.p.rapidapi.com"
CACHE_DIR = "data/cache"
DRAWS_CACHE_TTL = 600  # seconds — draws change during a live tournament

HEADERS = {
    "Content-Type": "application/json",
    "x-rapidapi-host": API_HOST,
    "x-rapidapi-key": API_KEY,
}

def _cache_path(name):
    return os.path.join(CACHE_DIR, name)

def _read_cache(path):
    with open(path, "r") as f:
        return json.load(f)

def _write_cache(path, data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# --- Draws: change during the tournament, so they get a TTL ---
def fetch_tournament_draws(tour, slug, year, include_all=True):
    url = f"https://{API_HOST}/tennis/v2/ms-api/tournament/{tour}/{slug}/{year}/draws"
    params = {"includeAll": str(include_all).lower()}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def get_draws_cached(tour, slug, year, force_refresh=False):
    path = _cache_path(f"{tour}_{slug}_{year}_draws.json")
    if not force_refresh and os.path.exists(path):
        age = time.time() - os.path.getmtime(path)
        if age < DRAWS_CACHE_TTL:
            print(f"draws: from cache (age {age:.0f}s)")
            return _read_cache(path)
        print(f"draws: cache stale (age {age:.0f}s) — refetching")
    print("draws: from API")
    data = fetch_tournament_draws(tour, slug, year)
    _write_cache(path, data)
    return data

# --- Surface history: historical, so cache permanently (no TTL) ---
def fetch_player_history(player_id, include_all=True):
    url = f"https://{API_HOST}/tennis/v2/atp/player/surface-summary/{player_id}"
    params = {"includeAll": str(include_all).lower()}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def get_history_cached(player_id, include_all=True):
    path = _cache_path(f"surface_history_{player_id}.json")
    if os.path.exists(path):
        return _read_cache(path)
    print(f"history: from API ({player_id})")
    data = fetch_player_history(player_id, include_all)
    _write_cache(path, data)
    return data