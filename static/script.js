async function fetchJSON(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }
    return response.json();
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
    } catch (err) {
        console.error("Failed to load draws:", err);
        container.textContent = "Failed to load the draw.";
    }
}

loadDraws();
