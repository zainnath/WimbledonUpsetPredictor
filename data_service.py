from models import Player, Match
from tennis_api import get_draws_cached, get_history_cached

def load_draw(force_refresh=False):
    """Build players + matches from the (cached) Wimbledon draw."""
    data = get_draws_cached("atp", "wimbledon", "2026", force_refresh=force_refresh)
    players, seen_ids, matches = [], set(), []
    for match in data["singles"]:
        for key in ("player1", "player2"):
            p = Player.from_api_dict(match[key])
            if p.id not in seen_ids:
                players.append(p)
                seen_ids.add(p.id)
        matches.append(Match.from_api_dict(match))
    players_by_id = {p.id: p for p in players}
    return players, matches, players_by_id

def compute_sets(players_by_id, matches):
    """Tally sets won/lost from completed match scores."""
    for m in matches:
        p1 = players_by_id.get(m.player1)
        p2 = players_by_id.get(m.player2)
        if p1 is None or p2 is None or not m.score or "-" not in m.score:
            continue
        for set_score in m.score.split(" "):
            if not set_score:
                continue
            games = set_score.split("(")[0].split("-")
            if len(games) != 2:
                continue
            try:
                p1_games, p2_games = int(games[0]), int(games[1])
            except ValueError:
                continue
            if p1_games > p2_games:
                p1.sets_won += 1
                p2.sets_lost += 1
            else:
                p2.sets_won += 1
                p1.sets_lost += 1

def get_grass_record(player_id):
    """(wins, losses) on grass, through the cached history."""
    data = get_history_cached(player_id)
    wins = losses = 0
    for year_entry in data["data"]:
        for surface in year_entry["surfaces"]:
            if surface["court"] == "Grass":
                wins += surface["courtWins"]
                losses += surface["courtLosses"]
    return wins, losses