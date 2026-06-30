class Player:

    def __init__(self, firstname, lastname, ranking, age, grass_wins_12mo, grass_loses_12mo, 
                 sets_won, sets_lost, H2H_wins, H2H_loses, H2H_grass_wins, H2H_grass_loses):
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

class Match:

    def __init__(self, player1, player2, round, winner, court, score):
        self.player1 = player1
        self.player2 = player2
        self.round = round
        self.winner = winner
        self.court = court
        self.score = score
    
    def upset_probability(self):
        pass

class Bracket:
    
    total_players = 0

    def __init__(self, matches):
        self.matches = matches

    def seeds_remaining():
        pass



player_1 = Player("Jannik", "Sinner", "1", "24", 20, 20, 3, 1, 5, 5, 4, 4)

print(player_1)

