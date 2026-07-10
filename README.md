# Wimbledon 2026 Upset Predictor

A small local web app that renders the live Wimbledon 2026 draw as a bracket,
predicts the odds of an upset for any matchup on click, and visualises serve
stats and win rates for the tournament's top seeds.

This is a personal, local-only project — it is not deployed anywhere.

![screenshot placeholder](docs/screenshot.png)

## What it does

- Renders the full draw as a round-by-round bracket (`/api/bracket` +
  `/api/players`), with a live text filter to find a player.
- Click any match card to get an on-demand upset probability
  (`/api/predict`), blending seed ranking, grass-court record, head-to-head
  history, and current-tournament form.
- Three Chart.js panels: average aces per top seed, aces vs. double faults
  per top seed, and win rate by player — all styled in Wimbledon green and
  purple, with per-section loading and error states so one failed chart never
  blocks the rest of the page.
- Degrades gracefully if the underlying tennis data API is unavailable or
  rate-limited: each section shows a friendly inline message instead of a
  broken page, while whatever data did load stays visible.

## Tech stack

- **Backend**: Python, Flask, `requests` (RapidAPI's
  `tennis-api-atp-wta-itf` for live draws and player surface history, cached
  to disk), `pandas` (historical ATP match data for head-to-head lookups),
  `python-dotenv` (local API key).
- **Frontend**: vanilla HTML/CSS/JS, no build step, no framework. Chart.js
  loaded via CDN.

## Local setup (Windows, conda)

1. Create/activate the conda environment:
   ```
   conda create -n sports-dashboard python=3.11
   conda activate sports-dashboard
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Add your RapidAPI key. Create a `.env` file in the project root (this file
   is gitignored and never committed):
   ```
   RAPIDAPI_KEY=your_key_here
   ```
   The key must be subscribed to the `tennis-api-atp-wta-itf` API on
   RapidAPI. A cached copy of the 2026 draw and player histories already
   ships in `data/cache/`, so the app runs even before you have a key —
   you'll only hit the live API on a cache miss (draws refresh every 10
   minutes) or if you pass `?refresh=true` to `/api/bracket`.
4. Run it **from the project root**. Flask's template/static paths resolve
   regardless of working directory, but `tennis_api.py`'s cache directory
   (`data/cache`) is a plain relative path, so it only finds the existing
   cache — and only writes new cache files in the right place — when you
   launch from the project root:
   ```
   python app.py
   ```
5. Open **http://127.0.0.1:5000/** in a browser.

## API endpoints

| Endpoint | Returns |
|---|---|
| `GET /api/bracket` | Draw grouped by round, with score/winner per match |
| `GET /api/players` | All players in the draw (id, name, seed, sets won/lost) |
| `GET /api/players/search?q=` | Players matching a name query |
| `GET /api/players/<id>` | One player's grass-court record and match history |
| `GET /api/predict?fav=&underdog=` | Upset probability for a matchup |
| `GET /api/h2h?p1=&p2=` | Head-to-head record between two players |
| `GET /api/seed-stats` | Avg. aces / double faults per match, top 8 seeds |

## The 14-day build story

This project was built incrementally, a day at a time:

- **Days 1–5**: Python fundamentals, file/error handling, NumPy/OOP, and
  pandas — working up to pulling historical match data from CSV.
- **Day 6**: First API integration; player surface-history caching and the
  grass-court record calculation.
- **Days 7–8**: The upset predictor itself — ranking, grass record, H2H, and
  form blended into a single weighted probability — plus the first Flask
  endpoints.
- **Days 9–10**: The bracket frontend — fetching the live draw and rendering
  it as a clickable, round-by-round grid.
- **Day 11**: Added Chart.js visualisations on top of the existing endpoints.
- **Day 12**: Wired the whole page into one coordinated load sequence, with
  section-level failure isolation so one broken fetch can't blank the page.
- **Day 13**: Swapped the upset-probability charts for serve-stat and
  win-rate charts, added a player filter, per-section loading states, a
  "last updated" timestamp, a consistent Wimbledon green/purple theme, and
  graceful handling of a down/rate-limited tennis API.
- **Day 14**: Packaged it as a documented, reproducible local project —
  this README, `requirements.txt`, a corrected `.gitignore`, and a secrets
  check.

## Notes

- No hosting/deployment configuration is included by design — this runs
  locally only.
- `debug=True` is set in `app.py` for local development; it should not be
  used as-is if this were ever deployed.
