import pandas as pd
import numpy as np
import json
from models import Player
from upset_predictor import upset_predictor

matches = pd.read_csv(r'C:\Users\Zain\OneDrive\FirstProject26\data\atp_matches_till_2022.csv')

def get_player_stats():
        with open("data/cache/atp_wimbledon_2026_draws.json", "r") as f:
            return json.load(f)

players = []
seen_ids = set()

data = get_player_stats()

for match in data["singles"]:
    player1 = Player.from_api_dict(match["player1"])
    player2 = Player.from_api_dict(match["player2"])
    
    if player1.id not in seen_ids:
        players.append(player1)
        seen_ids.add(player1.id)
    
    if player2.id not in seen_ids:
        players.append(player2)
        seen_ids.add(player2.id)

fav = 'Jannik Sinner'
underdog = 'Ignacio Buse'

player1 = next((p for p in players if p.name == fav), None)
player2 = next((p for p in players if p.name == underdog), None)

if player1.ranking is None:
    player1_ranking = 100000
else: 
    player1_ranking = int(player1.ranking)
if player2.ranking is None:
    player2_ranking = 100000
else:
    player2_ranking = int(player2.ranking)


result = upset_predictor(player1_ranking, player2_ranking, player1, player2, matches)

print(result)
