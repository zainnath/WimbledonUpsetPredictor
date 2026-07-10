async function fetchJSON(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }
    return response.json();
}

function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

// Toggles a chart between its loading/error status text and its canvas, so a
// chart never shows a blank flash and a failed fetch never leaves it stuck
// on "Loading…".
function setChartStatus(canvasId, message) {
    const canvas = document.getElementById(canvasId);
    const status = canvas.parentElement.querySelector(".status-message");
    if (message) {
        status.textContent = message;
        status.hidden = false;
        canvas.hidden = true;
    } else {
        status.hidden = true;
        canvas.hidden = false;
    }
}

function seedLabel(seed) {
    return seed != null ? `#${seed}` : "—";
}

function getSeed(playersById, playerId) {
    const ranking = playersById.get(playerId)?.ranking;
    if (ranking == null) return null;
    const seed = Number(ranking);
    return Number.isNaN(seed) ? null : seed;
}

function matchCardHTML(match, playersById) {
    const p1Seed = getSeed(playersById, match.player1_id);
    const p2Seed = getSeed(playersById, match.player2_id);
    const p1Winner = match.winner_id === match.player1_id;
    const p2Winner = match.winner_id === match.player2_id;

    return `
        <div class="match"
             data-p1-id="${match.player1_id}" data-p1-name="${match.player1}"
             data-p2-id="${match.player2_id}" data-p2-name="${match.player2}">
            <div class="player ${p1Winner ? "winner" : ""}">
                <span class="seed">${seedLabel(p1Seed)}</span>
                <span class="name">${match.player1}</span>
            </div>
            <div class="player ${p2Winner ? "winner" : ""}">
                <span class="seed">${seedLabel(p2Seed)}</span>
                <span class="name">${match.player2}</span>
            </div>
            <div class="score">${match.score || "Not yet played"}</div>
            <div class="prediction"></div>
        </div>
    `;
}

function renderBracket(container, rounds, playersById) {
    container.innerHTML = "";
    for (const round of rounds) {
        const column = document.createElement("div");
        column.className = "round";
        column.dataset.roundId = round.round_id;

        const heading = document.createElement("h2");
        heading.textContent = round.round;
        column.appendChild(heading);

        for (const match of round.matches) {
            column.insertAdjacentHTML("beforeend", matchCardHTML(match, playersById));
        }

        container.appendChild(column);
    }
}

// Lower seed number wins the favourite slot; falls back to whichever side is
// seeded if only one is, and to player1 if neither is (the unseeded-vs-unseeded
// dead zone — the API still needs two names, so this pairing is a low-confidence guess).
function pickFavourite(p1Name, p1Seed, p2Name, p2Seed) {
    if (p1Seed != null && p2Seed != null) {
        return p1Seed <= p2Seed ? [p1Name, p2Name] : [p2Name, p1Name];
    }
    if (p1Seed != null) return [p1Name, p2Name];
    if (p2Seed != null) return [p2Name, p1Name];
    return [p1Name, p2Name];
}

async function handleMatchClick(event, playersById) {
    const card = event.target.closest(".match");
    if (!card) return;

    const predictionEl = card.querySelector(".prediction");
    if (!predictionEl || predictionEl.dataset.loaded === "true") return;

    const p1Id = Number(card.dataset.p1Id);
    const p2Id = Number(card.dataset.p2Id);
    const p1Seed = getSeed(playersById, p1Id);
    const p2Seed = getSeed(playersById, p2Id);
    const [fav, underdog] = pickFavourite(
        card.dataset.p1Name, p1Seed, card.dataset.p2Name, p2Seed
    );

    predictionEl.textContent = "Predicting…";
    predictionEl.dataset.loaded = "pending";

    try {
        const params = new URLSearchParams({ fav, underdog });
        const result = await fetchJSON(`/api/predict?${params}`);
        const prob = result.upset_probability;

        if (typeof prob !== "number" || Number.isNaN(prob)) {
            predictionEl.textContent = "Prediction unavailable";
            predictionEl.dataset.loaded = "false";
        } else {
            predictionEl.textContent = `Upset chance (${underdog}): ${(prob * 100).toFixed(1)}%`;
            predictionEl.dataset.loaded = "true";
        }
    } catch (err) {
        console.error("Prediction failed:", err);
        predictionEl.textContent = "Prediction unavailable";
        predictionEl.dataset.loaded = "false";
    }
}

// Win rate isn't exposed by any endpoint, but /api/bracket already carries
// player1_id/player2_id/winner_id for every match, so it's computed here from
// data loadDraws() already fetched rather than adding a backend aggregation.
function computeWinRates(rounds, playersById) {
    const tally = new Map(); // player id -> {played, won}
    for (const round of rounds) {
        for (const match of round.matches) {
            if (match.winner_id == null) continue; // unplayed or unparseable
            for (const id of [match.player1_id, match.player2_id]) {
                const t = tally.get(id) || { played: 0, won: 0 };
                t.played += 1;
                if (id === match.winner_id) t.won += 1;
                tally.set(id, t);
            }
        }
    }
    return Array.from(tally.entries())
        .map(([id, t]) => ({
            name: playersById.get(id)?.name ?? String(id),
            played: t.played,
            winRate: t.won / t.played,
        }))
        .filter((p) => p.played >= 2) // a single-match record isn't a meaningful rate
        .sort((a, b) => b.winRate - a.winRate || b.played - a.played)
        .slice(0, 10);
}

async function loadDraws() {
    const container = document.getElementById("bracket");
    try {
        const [bracketData, playersData] = await Promise.all([
            fetchJSON("/api/bracket"),
            fetchJSON("/api/players"),
        ]);

        const playersById = new Map(playersData.players.map((p) => [p.id, p]));
        renderBracket(container, bracketData.rounds, playersById);
        container.addEventListener("click", (event) => handleMatchClick(event, playersById));

        renderWinRate(bracketData.rounds, playersById);
    } catch (err) {
        console.error("Failed to load draws:", err);
        container.innerHTML = '<p class="status-message">Couldn\'t load the draw — the tennis data source may be unavailable. Try refreshing.</p>';
        setChartStatus("winRateChart", "Win rate unavailable — draw data didn't load.");
    }
}

let seedStatsChart = null;
let acesDoubleFaultsChart = null;
let winRateChart = null;

function renderSeedStats(seeds) {
    const labels = seeds.map((s) => `#${s.seed} ${s.name}`);
    const data = seeds.map((s) => s.avg_aces);

    if (seedStatsChart) seedStatsChart.destroy();
    const ctx = document.getElementById("seedStatsChart");
    seedStatsChart = new Chart(ctx, {
        type: "bar",
        data: { labels, datasets: [{ label: "Avg. aces per match", data, backgroundColor: cssVar("--accent-green") }] },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { beginAtZero: true } },
        },
    });
}

function renderAcesDoubleFaults(seeds) {
    const labels = seeds.map((s) => `#${s.seed} ${s.name}`);
    const aces = seeds.map((s) => s.avg_aces);
    const doubleFaults = seeds.map((s) => s.avg_double_faults);

    if (acesDoubleFaultsChart) acesDoubleFaultsChart.destroy();
    const ctx = document.getElementById("acesDoubleFaultsChart");
    acesDoubleFaultsChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [
                { label: "Aces", data: aces, backgroundColor: cssVar("--accent-green") },
                { label: "Double faults", data: doubleFaults, backgroundColor: cssVar("--accent-purple") },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { beginAtZero: true } },
        },
    });
}

async function loadServeStatsCharts() {
    try {
        const data = await fetchJSON("/api/seed-stats");
        renderSeedStats(data.seeds);
        renderAcesDoubleFaults(data.seeds);
        setChartStatus("seedStatsChart", null);
        setChartStatus("acesDoubleFaultsChart", null);
    } catch (err) {
        console.error("Failed to load seed stats:", err);
        setChartStatus("seedStatsChart", "Serve stats unavailable right now.");
        setChartStatus("acesDoubleFaultsChart", "Serve stats unavailable right now.");
    }
}

function renderWinRate(rounds, playersById) {
    const players = computeWinRates(rounds, playersById);
    if (!players.length) {
        setChartStatus("winRateChart", "Not enough completed matches yet.");
        return;
    }

    const labels = players.map((p) => p.name);
    const data = players.map((p) => Math.round(p.winRate * 1000) / 10);

    if (winRateChart) winRateChart.destroy();
    const ctx = document.getElementById("winRateChart");
    winRateChart = new Chart(ctx, {
        type: "bar",
        data: { labels, datasets: [{ label: "Win rate (%)", data, backgroundColor: cssVar("--accent-green") }] },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { beginAtZero: true, max: 100 } },
        },
    });
    setChartStatus("winRateChart", null);
}

function setupFilter() {
    const input = document.getElementById("playerFilter");
    if (!input) return;
    input.addEventListener("input", () => {
        const query = input.value.trim().toLowerCase();
        document.querySelectorAll(".match").forEach((card) => {
            const p1 = card.dataset.p1Name.toLowerCase();
            const p2 = card.dataset.p2Name.toLowerCase();
            const isMatch = !query || p1.includes(query) || p2.includes(query);
            card.classList.toggle("filtered-out", !isMatch);
        });
    });
}

function updateLastUpdated() {
    const el = document.getElementById("lastUpdated");
    if (!el) return;
    const time = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    el.textContent = `Last updated ${time}`;
}

// Single entry point: the bracket and each chart fetch/render independently,
// so one section failing (e.g. a chart endpoint erroring) never blocks the
// rest of the page from rendering.
async function initApp() {
    updateLastUpdated();
    setupFilter();
    const sections = await Promise.allSettled([
        loadDraws(),
        loadServeStatsCharts(),
    ]);
    sections.forEach((result) => {
        if (result.status === "rejected") {
            console.error("A section failed to load:", result.reason);
        }
    });
}

initApp();
