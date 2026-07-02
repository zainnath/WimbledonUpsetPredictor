import pandas as pd

matches = pd.read_csv(r'C:\Users\Zain\OneDrive\FirstProject26\data\atp_matches_till_2022.csv')

def get_player_wins(player, matches):
    
    grass_matches = matches[matches['surface'] == 'Grass']
    player_wins = grass_matches[grass_matches['winner_name'] == player]
    return len(player_wins)

def get_player_losses(player, matches):

    grass_matches = matches[matches['surface'] == 'Grass']
    player_losses = grass_matches[grass_matches['loser_name'] == player]
    return len(player_losses)

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
    
def grass_record(fav, underdog, matches):
    wins_grass_fav = get_player_wins(fav, matches)
    losses_grass_fav = get_player_losses(fav, matches)
    total_grass_fav = wins_grass_fav + losses_grass_fav

    wins_grass_underdog = get_player_wins(underdog, matches)
    losses_grass_underdog = get_player_losses(underdog, matches)
    total_grass_underdog = wins_grass_underdog + losses_grass_underdog
    print(total_grass_underdog)
    print(total_grass_fav)
    if total_grass_fav != 0:
        fav_result = wins_grass_fav/total_grass_fav
    else:
        fav_result = 0
    
    if total_grass_underdog != 0:
        underdog_result = wins_grass_underdog/total_grass_underdog
    else:
        underdog_result = 0
    
    
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

def form(underdog_sets_total, underdog_sets_wins, fav_sets_total, fav_sets_wins):
    if underdog_sets_total > 0 & fav_sets_total > 0:
        underdog_win_rate = underdog_sets_wins/underdog_sets_total
        fav_win_rate = fav_sets_wins/fav_sets_total

        if underdog_win_rate > fav_win_rate:
            return 1
        elif underdog_win_rate == fav_win_rate:
            return 0
        else:
            return underdog_win_rate/fav_win_rate
    else:
        return 0
    

def upset_predictor(rank_fav, rank_underdog, fav, underdog, matches, underdog_sets_total = 0, underdog_sets_wins = 0, fav_sets_total = 0, fav_sets_wins = 0):
    factor1 = ranking_factor(rank_fav, rank_underdog)
    factor2 = grass_record(fav, underdog, matches)
    factor3 = h2h(fav, underdog, matches)
    factor4 = form(underdog_sets_total, underdog_sets_wins, fav_sets_total, fav_sets_wins)

    #print(factor1)
    print(factor2)
    #print(factor3)

    if factor4 > 0:
        return 0.1*factor1 + 0.5*factor2 + 0.1*factor3 + 0.3*factor4
    else: 
        return 0.1*factor1 + 0.7*factor2 + 0.2*factor3
    
grass_record('Jannik Sinner', 'Ignacio Buse', matches)