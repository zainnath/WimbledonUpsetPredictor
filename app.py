from flask import Flask, jsonify, request
from data_service import load_draw, compute_sets
from predict import predict_matchup

app = Flask(__name__)

@app.route("/draws")
def draws():
    force = request.args.get("refresh") == "true"
    players, matches, players_by_id = load_draw(force_refresh=force)
    compute_sets(players_by_id, matches)   # ← tally before serializing
    return jsonify({
        "players": [p.to_dict() for p in players],
        "matches": [m.to_dict() for m in matches],
    })

@app.route("/predict")
def predict():
    try:
        prob = predict_matchup(request.args.get("fav"), request.args.get("underdog"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify({"upset_probability": prob})

if __name__ == "__main__":
    app.run(debug=True)
    