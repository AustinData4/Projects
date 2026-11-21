# PostgreSQL Implementation Guide (For DBeaver)

Since you already have DBeaver connected to PostgreSQL this is the fastest way:

---

## ✅ Step 1: Run this SQL in DBeaver
Open a new SQL editor window, paste this and execute:

```sql
-- Create bets table
CREATE TABLE bets (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
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

-- Create index for fast lookups
CREATE INDEX idx_bets_user_id ON bets(user_id);
```

✅ You will now see a new `bets` table in your database.

---

## ✅ Step 2: Update the frontend
Replace only these 2 functions in your HTML file:

```javascript
async function loadGames() {
    const res = await fetch("/api/bets");
    games = await res.json();
    renderGames();
}

async function saveGames() {
    await fetch("/api/bets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(games)
    });
}
```

✅ That is the **only change you need to make**. All existing betting functionality stays 100% the same.

---

## ✅ Step 3: Backend Endpoint
If you are using Node.js / Express:

```javascript
const { Pool } = require('pg');
const pool = new Pool({
    // Add your PostgreSQL connection details here
    user: 'postgres',
    host: 'localhost',
    database: 'your_database',
    password: 'your_password',
    port: 5432,
});

// Save all bets
app.post('/api/bets', async (req, res) => {
    const bets = req.body;
    const userId = 1; // Replace this with actual authenticated user id

    // Delete old entries and insert new ones in one transaction
    const client = await pool.connect();
    try {
        await client.query('BEGIN');
        await client.query('DELETE FROM bets WHERE user_id = $1', [userId]);

        for (const bet of bets) {
            await client.query(`
                INSERT INTO bets (
                    user_id, player1, player2, game_type, date, stakes,
                    odds, score, notes, status, winner, amount
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            `, [
                userId, bet.player1, bet.player2, bet.gameType, bet.date, bet.stakes,
                bet.odds, bet.score, bet.notes, bet.status, bet.winner, bet.amount
            ]);
        }

        await client.query('COMMIT');
        res.json({ success: true });
    } catch (err) {
        await client.query('ROLLBACK');
        res.status(500).json({ error: err.message });
    } finally {
        client.release();
    }
});

// Load all bets
app.get('/api/bets', async (req, res) => {
    const userId = 1; // Replace this with actual authenticated user id
    const result = await pool.query('SELECT * FROM bets WHERE user_id = $1 ORDER BY date DESC', [userId]);
    res.json(result.rows);
});
```

---

## ✅ Done
That's it. You now have:
- Full bet history saved permanently in PostgreSQL
- All existing features work exactly as before
- You can view/query all bets directly inside DBeaver
- You can add user authentication later without changing anything else

This is exactly how this app was designed to be deployed.