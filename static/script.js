async function loadDraws() {
    try {
        const response = await fetch("/api/bracket");
        if (!response.ok) {
            throw new Error(`Request failed: ${response.status}`);
        }
        const data = await response.json();
        console.log(data);

        const container = document.getElementById("draws");
        for (const round of data.rounds) {
            for (const match of round.matches) {
                const line = document.createElement("p");
                line.textContent = `${round.round}: ${match.player1} vs ${match.player2} — ${match.score} (winner: ${match.winner})`;
                container.appendChild(line);
            }
        }
    } catch (err) {
        console.error("Failed to load draws:", err);
    }
}

loadDraws();
