from dotenv import load_dotenv
import os
import requests
import json
from models import Player, Match

load_dotenv()  # reads .env and loads its contents into the environment

api_key = os.getenv("RAPIDAPI_KEY")

def get_player_stats():
        with open("data/cache/atp_wimbledon_2026_draws.json", "r") as f:
            return json.load(f)

CACHE_DIR = "data/cache"

def fetch_tournament_draws(tour, slug, year, include_all=True):
    url = f"https://tennis-api-atp-wta-itf.p.rapidapi.com/tennis/v2/ms-api/tournament/{tour}/{slug}/{year}/draws"

    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": "tennis-api-atp-wta-itf.p.rapidapi.com",
        "x-rapidapi-key": api_key
    }

    params = {
        "includeAll": str(include_all).lower()
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()


def get_draws_cached(tour, slug, year):
    cache_path = f"{CACHE_DIR}/{tour}_{slug}_{year}_draws.json"

    if os.path.exists(cache_path):
        print("from cache")
        with open(cache_path, "r") as f:
            return json.load(f)

    print("from API")
    data = fetch_tournament_draws(tour, slug, year)
    print("Updated matches!")

    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump(data, f, indent=2)

    return data


players_2026 = []
seen_ids = set()
matches = []

data = get_player_stats()

for match in data["singles"]:
    player1 = Player.from_api_dict(match["player1"])
    player2 = Player.from_api_dict(match["player2"])
    
    
    if player1.id not in seen_ids:
        players_2026.append(player1)
        seen_ids.add(player1.id)
    
    if player2.id not in seen_ids:
        players_2026.append(player2)
        seen_ids.add(player2.id)

for match in data["singles"]:
    matches.append(match)


def fetch_player_history(player_id, include_all=True):
    url = f"https://tennis-api-atp-wta-itf.p.rapidapi.com/tennis/v2/atp/player/surface-summary/{player_id}"

    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": "tennis-api-atp-wta-itf.p.rapidapi.com",
        "x-rapidapi-key": api_key
    }

    params = {
        "includeAll": str(include_all).lower()
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()


def get_history_cached(player_id, include_all=True):
    cache_path = f"{CACHE_DIR}/surface_history_{player_id}.json"

    if os.path.exists(cache_path):
        print("from cache")
        with open(cache_path, "r") as f:
            return json.load(f)

    print("from API")
    data = fetch_player_history(player_id, include_all)

    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump(data, f, indent=2)

    return data

player_histories = {}

for player in players_2026:
    try:
        history = get_history_cached(player.id)
        player_histories[player.id] = history
    except requests.exceptions.HTTPError as e:
        print(f"Failed for {player.name} (ID {player.id}): {e}")


