import os
import pandas as pd
from upset_predictor import upset_predictor
from data_service import load_draw, compute_sets, get_grass_record, find_player
 
# anchored to this file's folder, so it works no matter where you run Python from
MATCHES_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "data", "atp_matches_till_2022.csv")
 
_historical = None  # loaded once, reused by every request
 
 
def get_historical():
    global _historical
    if _historical is None:
        _historical = pd.read_csv(MATCHES_CSV)
    return _historical
 
 
def _safe_ranking(player):
    return int(player.ranking) if player.ranking is not None else 100000
 
 
def predict_matchup(fav_name, underdog_name, force_refresh=False):
    players, matches, players_by_id = load_draw(force_refresh=force_refresh)
    compute_sets(players_by_id, matches)
 
    fav = find_player(players, fav_name)
    dog = find_player(players, underdog_name)
    if fav is None or dog is None:
        missing = fav_name if fav is None else underdog_name
        raise ValueError(f"Player not found in draw: {missing}")
 
    fav_gw, fav_gl = get_grass_record(int(fav.id))
    dog_gw, dog_gl = get_grass_record(int(dog.id))
 
    prob, factors = upset_predictor(
        _safe_ranking(fav), _safe_ranking(dog),
        fav.name, dog.name, get_historical(),
        fav_gw, fav_gl, dog_gw, dog_gl,
        fav.sets_won, fav.sets_lost, dog.sets_won, dog.sets_lost,
    )
 
    return {
        "favourite": fav.name,
        "underdog": dog.name,
        "upset_probability": round(prob, 4),
        "factors": {k: round(v, 4) for k, v in factors.items()},
    }
 
 
if __name__ == "__main__":
    result = predict_matchup("Jannik Sinner", "Ignacio Buse")
    print(f"{result['upset_probability'] * 100:.1f}%")