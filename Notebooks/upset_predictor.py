import pandas as pd

matches = pd.read_csv(r'C:\Users\Zain\OneDrive\FirstProject26\data\atp_matches_till_2022.csv')


def h2h_total(fav, underdog, matches):   
    h2h_matches1 = matches[(matches['winner_name'] == fav) & (matches['loser_name'] == underdog)]
    h2h_matches2 = matches[(matches['loser_name'] == fav) & (matches['winner_name'] == underdog)]

    h2h_total = len(h2h_matches1) + len(h2h_matches2)

    h2h_underdog_wins = matches[(matches['loser_name'] == fav) & (matches['winner_name'] == underdog)]

    return h2h_total, len(h2h_underdog_wins)

def ranking_factor(rank_fav, rank_underdog):
    if rank_fav is None or rank_underdog is None:
        return 0
    else:
        return rank_fav/rank_underdog
    
def grass_record(grass_wins_fav, grass_losses_fav, grass_wins_underdog, grass_losses_underdog):

    total_grass_fav = grass_wins_fav + grass_losses_fav

    total_grass_underdog = grass_wins_underdog + grass_losses_underdog

    if total_grass_fav != 0:
        fav_result = grass_wins_fav/total_grass_fav
    else:
        fav_result = 0
    
    if total_grass_underdog != 0:
        underdog_result = grass_wins_underdog/total_grass_underdog
    else:
        underdog_result = 0


    min_matches = 5
    fav_confidence = min(total_grass_fav / min_matches, 1)
    underdog_confidence = min(total_grass_underdog / min_matches, 1)

    fav_result = 0.5 + (fav_result - 0.5) * fav_confidence
    underdog_result = 0.5 + (underdog_result - 0.5) * underdog_confidence
    
    if underdog_result >= fav_result:
        return 1
    elif underdog_result == 0:
        return 0
    else:
        return underdog_result/fav_result
    
def h2h(fav, underdog, matches):

    total_matches, underdog_wins = h2h_total(fav, underdog, matches)
    if total_matches != 0:
        if underdog_wins == total_matches:
            return 1
        else:
            return underdog_wins/total_matches
    else:
        return 0

def form(fav_sets_won, fav_sets_lost, underdog_sets_won, underdog_sets_lost):
    underdog_sets_total = underdog_sets_won + underdog_sets_lost
    fav_sets_total = fav_sets_won + fav_sets_lost
    if (underdog_sets_total > 0) and (fav_sets_total) > 0:
        underdog_win_rate = underdog_sets_won/underdog_sets_total
        fav_win_rate = fav_sets_won/fav_sets_total
        if underdog_win_rate > fav_win_rate:
            return 1
        elif underdog_win_rate == fav_win_rate:
            return 0
        else:
            return underdog_win_rate/fav_win_rate
    else:
        return 0
    

def upset_predictor(rank_fav, rank_underdog, fav, underdog, matches, grass_wins_fav, grass_losses_fav, grass_wins_underdog, grass_losses_underdog, fav_sets_won = 0, fav_sets_lost = 0, underdog_sets_won = 0, underdog_sets_lost = 0):
    factor1 = ranking_factor(rank_fav, rank_underdog)
    factor2 = grass_record(grass_wins_fav, grass_losses_fav, grass_wins_underdog, grass_losses_underdog)
    factor3 = h2h(fav, underdog, matches)
    factor4 = form(fav_sets_won, fav_sets_lost, underdog_sets_won, underdog_sets_lost)

    print(factor1)
    print(factor2)
    print(factor3)
    print(factor4)

    if factor4 > 0:
        return 0.3*factor1 + 0.3*factor2 + 0.2*factor3 + 0.2*factor4
    
    
