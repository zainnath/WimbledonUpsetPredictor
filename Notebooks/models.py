class Player:

    def __init__(self, id, name, ranking, age=0, grass_wins_12mo=0, grass_loses_12mo=0, 
                 sets_won=0, sets_lost=0, H2H_wins=0, H2H_loses=0):
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
    def from_api_dict(cls, data1):
        return cls(id = data1["id"], name = data1["name"], ranking = data1["seed"])



class Match:

    def __init__(self, player1, player2, roundId, score, winner = None):
        self.player1 = player1
        self.player2 = player2
        self.roundId = roundId
        self.winner = winner
        self.score = score

    def __repr__(self):
        return "{} vs {}".format(self.player1, self.player2)
    
    def upset_probability(self):
        pass

    @classmethod
    def from_api_dict(cls, data1):
        return cls(player1 = data1["player1Id"], player2 = data1["player2Id"], 
             score = data1["result"], roundId = data1["roundId"])

class Bracket:
    
    total_players = 0

    def __init__(self, matches):
        self.matches = matches

    def seeds_remaining():
        pass
    