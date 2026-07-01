import pandas as pd
import numpy as np

class Player:

    def __init__(self, firstname, lastname, ranking, age=0, grass_wins_12mo=0, grass_loses_12mo=0, 
                 sets_won=0, sets_lost=0, H2H_wins=0, H2H_loses=0, H2H_grass_wins=0, H2H_grass_loses=0):
        self.firstname = firstname
        self.lastname = lastname
        self.ranking = ranking
        self.age = age
        self.grass_wins_12mo = grass_wins_12mo
        self.grass_loses_12mo = grass_loses_12mo
        self.sets_won = sets_won
        self.sets_lost = sets_lost
        self.H2H_wins = H2H_wins
        self.H2H_loses = H2H_loses
        self.H2H_grass_wins = H2H_grass_wins
        self.H2H_grass_loses = H2H_grass_loses
    
    def __repr__(self):
        return "{} {} - ranked number {}".format(self.firstname, self.lastname, self.ranking)

    @property
    def grass_win_rate(self):
        percent_wins = (self.grass_wins_12mo / (self.grass_wins_12mo + self.grass_loses_12mo)) * 100 
        return "{}+%".format(percent_wins)

    @classmethod
    def from_api_dict(cls, data):
        return cls(firstname = data["firstname"], 
                   lastname = data["lastname"], 
                   ranking = data["ranking"])



class Match:

    def __init__(self, player1, player2, round, winner, court, score):
        self.player1 = player1
        self.player2 = player2
        self.round = round
        self.winner = winner
        self.court = court
        self.score = score

    def __repr__(self):
        return "{} vs {}".format(self.player1, self.player2)
    
    def upset_probability(self):
        pass

class Bracket:
    
    total_players = 0

    def __init__(self, matches):
        self.matches = matches

    def seeds_remaining():
        pass

matches = pd.read_csv(r'C:\Users\Zain\OneDrive\FirstProject26\data\atp_matches_till_2022.csv')

def get_player_wins(player, matches):
    
    grass_matches = matches[matches['surface'] == 'Grass']
    player_wins = grass_matches[grass_matches['winner_name'] == player]
    return len(player_wins)

def get_player_losses(player, matches):

    grass_matches = matches[matches['surface'] == 'Grass']
    player_losses = grass_matches[grass_matches['loser_name'] == player]
    return len(player_losses)


def ranking_factor(rank_underdog, rank_fav):
    return rank_fav/rank_underdog
    
def grass_record(fav, underdog, matches):
    wins_grass_fav = get_player_wins(fav, matches)
    losses_grass_fav = get_player_losses(fav, matches)
    total_grass_fav = wins_grass_fav + losses_grass_fav

    wins_grass_underdog = get_player_wins(underdog, matches)
    losses_grass_underdog = get_player_losses(underdog, matches)
    total_grass_underdog = wins_grass_underdog + losses_grass_underdog

    if total_grass_fav != 0:
        fav_result = wins_grass_fav/total_grass_fav
    else:
        fav_result = 0
    
    if total_grass_underdog != 0:
        underdog_result = wins_grass_underdog/total_grass_underdog
    else:
        underdog_result = 0

    min_matches = 10
    fav_confidence = min(total_grass_fav / min_matches, 1)
    underdog_confidence = min(total_grass_underdog / min_matches, 1)

    fav_result = 0.5 + (fav_result - 0.5) * fav_confidence
    underdog_result = 0.5 + (underdog_result - 0.5) * underdog_confidence
    
    if underdog_result >= fav_result:
        return 1
    elif underdog_result == 0:
        return 0
    else:
        print(wins_grass_fav, total_grass_fav, wins_grass_underdog, total_grass_underdog)
        return underdog_result/fav_result
    
def h2h(total_matches, underdog_wins):
    if total_matches != 0:
        if underdog_wins == total_matches:
            return 1
        else:
            return underdog_wins/total_matches

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
    
    
    
def upset_predictor(rank_underdog, rank_fav, wins_grass_fav, total_grass_fav, wins_grass_underdog, total_grass_underdog, 
                    total_matches, underdog_wins, underdog_sets_total, underdog_sets_wins, fav_sets_total, fav_sets_wins):
    factor1 = ranking_factor(rank_underdog, rank_fav)
    factor2 = grass_record(wins_grass_fav, total_grass_fav, wins_grass_underdog, total_grass_underdog)
    factor3 = h2h(total_matches, underdog_wins)
    factor4 = form(underdog_sets_total, underdog_sets_wins, fav_sets_total, fav_sets_wins)
    if factor4 > 0:
        return 0.1*factor1 + 0.5*factor2 + 0.1*factor3 + 0.3*factor4
    else: 
        return 0.1*factor1 + 0.7*factor2 + 0.2*factor3


print(grass_record('Roger Federer', 'Rafael Nadal', matches))
