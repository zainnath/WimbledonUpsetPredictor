from models import Player, Match
from tennis_api import get_draws_cached, get_history_cached
 
ROUND_NAMES = {
    4: "Round of 128",
    5: "Round of 64",
    6: "Round of 32",
    7: "Round of 16",
    9: "Quarter-final",
    10: "Semi-final",
    11: "Final"}
 
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
 
 
def parse_sets(score):
    """Turn a score string like '6-4 7-6(3)' into [(6, 4), (7, 6)]. Skips junk."""
    if not score or "-" not in score:
        return []
    sets = []
    for token in score.split(" "):
        if not token:
            continue
        games = token.split("(")[0].split("-")
        if len(games) != 2:
            continue
        try:
            sets.append((int(games[0]), int(games[1])))
        except ValueError:
            continue
    return sets
 
 
def compute_sets(players_by_id, matches):
    """Tally sets won/lost from completed match scores."""
    for m in matches:
        p1 = players_by_id.get(m.player1)
        p2 = players_by_id.get(m.player2)
        if p1 is None or p2 is None:
            continue
        for p1_games, p2_games in parse_sets(m.score):
            if p1_games > p2_games:
                p1.sets_won += 1
                p2.sets_lost += 1
            else:
                p2.sets_won += 1
                p1.sets_lost += 1
 
 
def determine_winner(match):
    """Return the winning player's id based on sets won, or None if not decided."""
    sets = parse_sets(match.score)
    p1_sets = sum(1 for a, b in sets if a > b)
    p2_sets = sum(1 for a, b in sets if b > a)
    if p1_sets == p2_sets:
        return None  # unplayed, in progress, or unparseable
    return match.player1 if p1_sets > p2_sets else match.player2
 
 
def _round_sort_key(round_id):
    try:
        return (0, int(round_id))
    except (TypeError, ValueError):
        return (1, str(round_id))
 
 
def bracket_by_round(matches, players_by_id):
    """Grouped by round, with names, score, and winner. Matches whose pairing is
    already known but haven't been played yet (e.g. an upcoming semi-final) are
    included too, with score/winner left blank, so the bracket shows what's next."""
    rounds = {}
    for m in matches:
        winner_id = determine_winner(m)
        m.winner = winner_id
        p1 = players_by_id.get(m.player1)
        p2 = players_by_id.get(m.player2)
        winner = players_by_id.get(winner_id) if winner_id is not None else None
        rounds.setdefault(m.roundId, []).append({
            "player1": p1.name if p1 else str(m.player1),
            "player2": p2.name if p2 else str(m.player2),
            "player1_id": m.player1,
            "player2_id": m.player2,
            "score": m.score,
            "winner": winner.name if winner else None,
            "winner_id": winner_id,
        })
    return [
        {"round": ROUND_NAMES.get(rid, f"Round {rid}"), "round_id": rid, "matches": ms}
        for rid, ms in sorted(rounds.items(), key=lambda kv: _round_sort_key(kv[0]))
    ]
 
 
def find_player(players, query):
    """Case-insensitive lookup: exact name first, then substring. None if no hit."""
    if not query:
        return None
    q = query.strip().lower()
    for p in players:
        if p.name.lower() == q:
            return p
    for p in players:
        if q in p.name.lower():
            return p
    return None
 
 
def search_players(players, query):
    """All players whose name contains the query (case-insensitive)."""
    q = (query or "").strip().lower()
    if not q:
        return []
    return [p for p in players if q in p.name.lower()]
 
 
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