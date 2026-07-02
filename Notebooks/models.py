class Player:

    def __init__(self, id, name, ranking, age=0, grass_wins_12mo=0, grass_loses_12mo=0, 
                 sets_won=0, sets_lost=0, H2H_wins=0, H2H_loses=0, H2H_grass_wins=0, H2H_grass_loses=0):
        self.id = id
        self.name = name
        self.ranking = ranking
        self.age = age
        self.grass_wins_12mo = grass_wins_12mo
        self.grass_loses_12mo = grass_loses_12mo
        self.sets_won = sets_won
        self.sets_lost = sets_lost
        
    
    def __repr__(self):
        return "{} {} - ranked number {}".format(self.id, self.name, self.ranking)

    @property
    def grass_win_rate(self):
        percent_wins = (self.grass_wins_12mo / (self.grass_wins_12mo + self.grass_loses_12mo)) * 100 
        return "{}+%".format(percent_wins)
    
    @classmethod
    def from_api_dict(cls, data):
        return cls(id = data["id"], name = data["name"], ranking = data["seed"])



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
    