
import requests
from flask import Flask, jsonify, render_template, request
from data_service import (load_draw, compute_sets, get_grass_record, determine_winner,
                          bracket_by_round, find_player, search_players, seed_serve_stats)
from predict import predict_matchup, get_historical
from upset_predictor import h2h_total

app = Flask(__name__)


# Every route eventually calls the RapidAPI tennis endpoint (directly or via a
# cached read). If that API is down or rate-limited, `requests` raises here
# instead of any individual route crashing with an unhandled 500.
@app.errorhandler(requests.exceptions.RequestException)
def handle_tennis_api_error(e):
    return jsonify({"error": "Tennis data source is unavailable right now. Please try again shortly."}), 503


@app.route("/")
def index():
    return render_template("index.html")


def get_state(force_refresh=False):
    """Load the draw and tally sets — shared setup for most endpoints."""
    players, matches, players_by_id = load_draw(force_refresh=force_refresh)
    compute_sets(players_by_id, matches)
    return players, matches, players_by_id
 
 
# ---- Endpoint 1: bracket (home page) ------------------------------------
# Completed matches only, grouped by round, winner + score included.
@app.route("/api/bracket")
def bracket():
    force = request.args.get("refresh") == "true"
    players, matches, players_by_id = get_state(force_refresh=force)
    return jsonify({"rounds": bracket_by_round(matches, players_by_id)})
 
 
# ---- Endpoint 2: all players (dropdowns / autocomplete on pages 2 & 3) ---
@app.route("/api/players")
def players_list():
    players, _, _ = get_state()
    return jsonify({"players": [p.to_dict() for p in players]})
 
 
# ---- Endpoint 3: player search (search boxes on pages 2 & 3) ------------
@app.route("/api/players/search")
def players_search():
    q = request.args.get("q", "")
    if not q.strip():
        return jsonify({"error": "Missing query parameter: q"}), 400
    players, _, _ = get_state()
    results = search_players(players, q)
    return jsonify({"query": q, "results": [p.to_dict() for p in results]})
 
 
# ---- Endpoint 4: single player stats (stats page) ------------------------
@app.route("/api/players/<int:player_id>")
def player_stats(player_id):
    players, matches, players_by_id = get_state()
    player = players_by_id.get(player_id)
    if player is None:
        return jsonify({"error": f"No player with id {player_id} in the draw"}), 404
 
    grass_wins, grass_losses = get_grass_record(player_id)
    grass_total = grass_wins + grass_losses
 
    played = []
    for m in matches:
        if player_id not in (m.player1, m.player2):
            continue
        opponent_id = m.player2 if m.player1 == player_id else m.player1
        opponent = players_by_id.get(opponent_id)
        winner_id = determine_winner(m)
        played.append({
            "round": m.roundId,
            "opponent": opponent.name if opponent else str(opponent_id),
            "score": m.score,
            "won": winner_id == player_id if winner_id is not None else None,
        })
 
    return jsonify({
        **player.to_dict(),
        "grass_wins": grass_wins,
        "grass_losses": grass_losses,
        "grass_win_rate": round(grass_wins / grass_total, 3) if grass_total else None,
        "matches": played,
    })
 
 
# ---- Endpoint 5: upset prediction (predict page) --------------------------
@app.route("/api/predict")
def predict():
    fav = request.args.get("fav")
    underdog = request.args.get("underdog")
    if not fav or not underdog:
        return jsonify({"error": "Both 'fav' and 'underdog' query parameters are required"}), 400
    try:
        result = predict_matchup(fav, underdog)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify(result)
 
 
# ---- Endpoint 6: head-to-head record (stats + predict pages) --------------
@app.route("/api/h2h")
def h2h():
    p1 = request.args.get("p1")
    p2 = request.args.get("p2")
    if not p1 or not p2:
        return jsonify({"error": "Both 'p1' and 'p2' query parameters are required"}), 400
 
    players, _, _ = get_state()
    player1 = find_player(players, p1)
    player2 = find_player(players, p2)
    if player1 is None or player2 is None:
        missing = p1 if player1 is None else p2
        return jsonify({"error": f"Player not found in draw: {missing}"}), 404
 
    total, p2_wins = h2h_total(player1.name, player2.name, get_historical())
    return jsonify({
        "player1": player1.name,
        "player2": player2.name,
        "total_matches": total,
        "player1_wins": total - p2_wins,
        "player2_wins": p2_wins,
    })
 
 
# ---- Endpoint 7: serve stats for the top seeds (charts page) --------------
@app.route("/api/seed-stats")
def seed_stats():
    return jsonify({"seeds": seed_serve_stats()})


if __name__ == "__main__":
    app.run(debug=True)