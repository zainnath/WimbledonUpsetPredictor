from flask import Flask, render_template, jsonify, request
#from tennis_api import get_bracket, get_matches, get_player_by_id  

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/draw")
def api_draw():
    # TODO: return bracket.to_dict(), wrapped in try/except
    ...

@app.route("/api/matches")
def api_matches():
    # TODO: read ?upsets_only=, filter, return list of match dicts
    ...

@app.route("/api/player/<player_id>")
def api_player(player_id):
    # TODO: look up, 404 if missing, else return player.to_dict()
    ...

@app.route("/api/upsets")
def api_upsets():
    # TODO: run/read your upset predictor, return sorted predictions
    ...

if __name__ == "__main__":
    app.run(debug=True)