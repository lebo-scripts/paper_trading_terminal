# Project 3: Simulated Paper Trading Terminal

This is an intermediate-level terminal application simulating an interactive stock brokerage paper trading console. It handles real-time ticker quotes, buying/selling validation rules, transaction logs, and persistent account state.

---

## 📈 What it Does
- **Interactive Terminal Console**: Reads continuous terminal prompt command inputs mimicking real shells.
- **Commands**:
  - `help`: View commands instructions.
  - `balance`: View cash balance.
  - `quote <ticker>`: Fetch real-time price using `yfinance`.
  - `buy <ticker> <quantity>`: Buy shares at market price (if cash is sufficient). Updates average purchase cost.
  - `sell <ticker> <quantity>`: Sell shares at market price (if owned quantity is sufficient).
  - `portfolio`: Display holdings table with average cost, market value, individual returns, and net worth.
  - `history`: Display history of transactions.
  - `exit`: Write current database state to file and exit shell loop.
- **Account State Engine**: Persists cash balance, transaction log history, and asset positions to `paper_trading_state.json`.

---

## 🚀 How to Run
Run from your terminal:
```bash
python3 paper_trading.py
```

---

## 🧪 Running Unit Tests
To run tests verifying buy/sell execution logic and funds checking:
```bash
python3 -m unittest test_paper_trading.py
```
