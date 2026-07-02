import pandas as pd
import numpy as np
import json
from models import Player, Match
from upset_predictor import upset_predictor

matches = pd.read_csv(r'C:\Users\Zain\OneDrive\FirstProject26\data\atp_matches_till_2022.csv')

def get_player_stats():
        with open("data/cache/atp_wimbledon_2026_draws.json", "r") as f:
            return json.load(f)
        
def get_player_history(id):
    with open("data/cache/surface_history_{}.json".format(id), "r") as f:
            return json.load(f)

players_2026 = []
players_history = []
seen_ids = set()

data1 = get_player_stats()

for match in data1["singles"]:
    player1 = Player.from_api_dict(match["player1"])
    player2 = Player.from_api_dict(match["player2"])
    
    if player1.id not in seen_ids:
        players_2026.append(player1)
        seen_ids.add(player1.id)
    
    if player2.id not in seen_ids:
        players_2026.append(player2)
        seen_ids.add(player2.id)

matches_played = []
for match in data1["singles"]:
    match_details = Match.from_api_dict(match)
    matches_played.append(match_details)

players_by_id = {p.id: p for p in players_2026}

for m in matches_played:
    p1 = players_by_id.get(m.player1)
    p2 = players_by_id.get(m.player2)

    if p1 is None or p2 is None:
        continue

    if not m.score or "-" not in m.score:
        continue  # skip unplayed / malformed matches

    sets = m.score.split(" ")
    for set_score in sets:
        if not set_score:
            continue  # skip empty entries from split, if any

        set_score_clean = set_score.split("(")[0]
        games = set_score_clean.split("-")

        if len(games) != 2:
            continue  # malformed set score, skip it

        p1_games = int(games[0])
        p2_games = int(games[1])

        if p1_games > p2_games:
            p1.sets_won += 1
            p2.sets_lost += 1
        else:
            p2.sets_won += 1
            p1.sets_lost += 1

fav = 'Felix Auger Aliassime'
underdog = 'Ben Shelton'

player1 = next((p for p in players_2026 if p.name == fav), None)
player2 = next((p for p in players_2026 if p.name == underdog), None)

if player1.ranking is None:
    player1_ranking = 100000
else: 
    player1_ranking = int(player1.ranking)
if player2.ranking is None:
    player2_ranking = 100000
else:
    player2_ranking = int(player2.ranking)


player1_id = int(player1.id)
player2_id = int(player2.id)


data2 = get_player_history(player1_id)

grass_wins_fav = 0
grass_losses_fav = 0

for year_entry in data2["data"]:
    for surface in year_entry["surfaces"]:
        if surface["court"] == "Grass":
            grass_wins_fav += surface["courtWins"]
            grass_losses_fav += surface["courtLosses"]


data3 = get_player_history(player2_id)

grass_wins_underdog = 0
grass_losses_underdog = 0

for year_entry in data3["data"]:
    for surface in year_entry["surfaces"]:
        if surface["court"] == "Grass":
            grass_wins_underdog += surface["courtWins"]
            grass_losses_underdog += surface["courtLosses"]


result = upset_predictor(player1_ranking, player2_ranking, player1, player2, matches, grass_wins_fav, grass_losses_fav, grass_wins_underdog, grass_losses_underdog, player1.sets_won, player1.sets_lost, player2.sets_won, player2.sets_lost)

print(str(result*100) + '%')
