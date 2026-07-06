def h2h_total(fav_name, underdog_name, matches):
    h2h_matches1 = matches[(matches['winner_name'] == fav_name) & (matches['loser_name'] == underdog_name)]
    h2h_matches2 = matches[(matches['loser_name'] == fav_name) & (matches['winner_name'] == underdog_name)]
 
    total = len(h2h_matches1) + len(h2h_matches2)
    underdog_wins = len(h2h_matches2)
 
    return total, underdog_wins
 
 
def ranking_factor(rank_fav, rank_underdog):
    if rank_fav is None or rank_underdog is None:
        return 0
    return rank_fav / rank_underdog
 
 
def grass_record(grass_wins_fav, grass_losses_fav, grass_wins_underdog, grass_losses_underdog):
    total_grass_fav = grass_wins_fav + grass_losses_fav
    total_grass_underdog = grass_wins_underdog + grass_losses_underdog
 
    fav_result = grass_wins_fav / total_grass_fav if total_grass_fav else 0
    underdog_result = grass_wins_underdog / total_grass_underdog if total_grass_underdog else 0
 
    # shrink toward 0.5 when a player has few grass matches
    min_matches = 5
    fav_confidence = min(total_grass_fav / min_matches, 1)
    underdog_confidence = min(total_grass_underdog / min_matches, 1)
 
    fav_result = 0.5 + (fav_result - 0.5) * fav_confidence
    underdog_result = 0.5 + (underdog_result - 0.5) * underdog_confidence
 
    if underdog_result >= fav_result:
        return 1
    return underdog_result / fav_result
 
 
def h2h(fav_name, underdog_name, matches):
    total_matches, underdog_wins = h2h_total(fav_name, underdog_name, matches)
    if total_matches == 0:
        return 0
    return underdog_wins / total_matches
 
 
def form(fav_sets_won, fav_sets_lost, underdog_sets_won, underdog_sets_lost):
    """Returns None when there's no form data yet (distinct from a genuine 0)."""
    underdog_sets_total = underdog_sets_won + underdog_sets_lost
    fav_sets_total = fav_sets_won + fav_sets_lost
    if underdog_sets_total > 0 and fav_sets_total > 0:
        underdog_win_rate = underdog_sets_won / underdog_sets_total
        fav_win_rate = fav_sets_won / fav_sets_total
        if underdog_win_rate >= fav_win_rate:
            return 1
        return underdog_win_rate / fav_win_rate
    return None
 
 
def upset_predictor(rank_fav, rank_underdog, fav_name, underdog_name, matches,
                    grass_wins_fav, grass_losses_fav,
                    grass_wins_underdog, grass_losses_underdog,
                    fav_sets_won=0, fav_sets_lost=0,
                    underdog_sets_won=0, underdog_sets_lost=0):
    factor1 = ranking_factor(rank_fav, rank_underdog)
    factor2 = grass_record(grass_wins_fav, grass_losses_fav,
                           grass_wins_underdog, grass_losses_underdog)
    factor3 = h2h(fav_name, underdog_name, matches)
    factor4 = form(fav_sets_won, fav_sets_lost, underdog_sets_won, underdog_sets_lost)
 
    factors = {
        "ranking": factor1,
        "grass": factor2,
        "h2h": factor3,
        "form": factor4,
    }
 
    if factor4 is not None:
        prob = 0.3 * factor1 + 0.3 * factor2 + 0.2 * factor3 + 0.2 * factor4
    else:
        # no form data yet (e.g. tournament hasn't started) — renormalise remaining weights
        prob = (0.3 * factor1 + 0.3 * factor2 + 0.2 * factor3) / 0.8
 
    return prob, factors
