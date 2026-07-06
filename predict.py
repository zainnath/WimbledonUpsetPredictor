import os
import pandas as pd
from upset_predictor import upset_predictor
from data_service import load_draw, compute_sets, get_grass_record

MATCHES_CSV = os.path.join("data", "atp_matches_till_2022.csv")

def _safe_ranking(player):
    return int(player.ranking) if player.ranking is not None else 100000

def predict_matchup(fav_name, underdog_name, force_refresh=False):
    players, matches, players_by_id = load_draw(force_refresh=force_refresh)
    compute_sets(players_by_id, matches)
    historical = pd.read_csv(MATCHES_CSV)

    fav = next((p for p in players if p.name == fav_name), None)
    dog = next((p for p in players if p.name == underdog_name), None)
    if fav is None or dog is None:
        missing = fav_name if fav is None else underdog_name
        raise ValueError(f"Player not found in draw: {missing}")

    fav_gw, fav_gl = get_grass_record(int(fav.id))
    dog_gw, dog_gl = get_grass_record(int(dog.id))

    return upset_predictor(
        _safe_ranking(fav), _safe_ranking(dog),
        fav, dog, historical,
        fav_gw, fav_gl, dog_gw, dog_gl,
        fav.sets_won, fav.sets_lost, dog.sets_won, dog.sets_lost,
    )

if __name__ == "__main__":
    print(f"{predict_matchup('Jannik Sinner', 'Ignacio Buse') * 100:.1f}%")