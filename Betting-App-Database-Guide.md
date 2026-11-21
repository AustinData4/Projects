# Place Your Bets App: Database Implementation Guide

## ✅ Current Storage
Right now all bet history is stored **only in the user's browser localStorage** using key `betskiGamesV3` as plain JSON array.

---

## ✅ Best Way To Implement On Your Website

### 🔹 Option 1: Minimal Change (Recommended)
Keep **100% of the existing frontend logic** exactly as it is. Only replace the 2 storage functions:

```javascript
// Replace localStorage with your backend API
async function loadGames() {
    const res = await fetch("/api/user/bets", { credentials: "include" });
    games = await res.json();
    renderGames();
}

async function saveGames() {
    await fetch("/api/user/bets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(games),
        credentials: "include"
    });
}
```

✅ No other changes required. All bet calculations, UI, resolve flows, odds logic stay completely unchanged.

---

### 🔹 Option 2: PostgreSQL Schema
For production database use this table structure:
```sql
CREATE TABLE bets (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    player1 VARCHAR(64) NOT NULL,
    player2 VARCHAR(64) NOT NULL,
    game_type VARCHAR(32) NOT NULL,
    date DATE,
    stakes TEXT,
    odds VARCHAR(16),
    score TEXT,
    notes TEXT,
    status VARCHAR(16) DEFAULT 'In Progress',
    winner VARCHAR(64),
    amount NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_bets_user_id ON bets(user_id);
```

---

### 🔹 Option 3: Node.js Backend Example
```javascript
// Express endpoint to save bets
app.post("/api/user/bets", auth, async (req, res) => {
    await db.query(`
        DELETE FROM bets WHERE user_id = $1;
        INSERT INTO bets (
            user_id, player1, player2, game_type, date,
            stakes, odds, score, notes, status, winner, amount
        ) VALUES ${req.body.map(b => `(
            ${req.user.id}, '${b.player1}', '${b.player2}', '${b.gameType}', '${b.date}',
            '${b.stakes}', '${b.odds}', '${b.score}', '${b.notes}', '${b.status}', '${b.winner}', ${b.amount}
        )`).join(",")}
    `);
    res.json({ ok: true });
});

app.get("/api/user/bets", auth, async (req, res) => {
    const bets = await db.query("SELECT * FROM bets WHERE user_id = $1 ORDER BY date DESC", [req.user.id]);
    res.json(bets.rows);
});
```

---

## ✅ Migration Strategy
1.  First add user authentication to your site
2.  Add the 2 simple API endpoints above
3.  Replace the 2 storage functions in the frontend
4.  All existing functionality remains 100% identical

This application was intentionally designed to separate storage completely from business logic so you can swap it out without touching anything else.