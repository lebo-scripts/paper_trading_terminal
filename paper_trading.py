# ==============================================================================
# PROJECT 3: Simulated Paper Trading Terminal (Intermediate Level)
# An interactive command terminal simulating live paper trading.
# Manages account state, processes buy/sell trades, and fetches live quotes.
# ==============================================================================

import json
import os
import yfinance as yf
from datetime import datetime

STATE_FILE = "paper_trading_state.json"

def load_state():
    """
    Loads account state from file or initializes with default values.
    """
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as file:
                return json.load(file)
        except Exception:
            pass
            
    # Default initial state
    return {
        "cash": 10000.0,
        "portfolio": {},  # e.g., {"AAPL": {"shares": 10.0, "avg_cost": 150.0}}
        "history": []     # list of transaction dicts
    }

def save_state(state):
    """
    Saves account state to a JSON file.
    """
    try:
        with open(STATE_FILE, "w") as file:
            json.dump(state, file, indent=4)
    except Exception as error:
        print(f"Error saving state: {error}")

def fetch_price(ticker):
    """
    Fetches the latest closing price of a ticker using yfinance.
    Returns float or None if ticker invalid/offline.
    """
    try:
        ticker_obj = yf.Ticker(ticker)
        history = ticker_obj.history(period="1d")
        if not history.empty:
            return float(history["Close"].iloc[-1])
    except Exception:
        pass
    return None

def execute_buy(state, ticker, shares):
    """
    Executes a stock buy trade, updating cash, portfolio, and transaction history.
    """
    if shares <= 0:
        print("Error: Shares quantity must be greater than zero.")
        return state
        
    price = fetch_price(ticker)
    if price is None:
        print(f"Error: Could not retrieve price for ticker '{ticker}'. Ensure ticker is valid.")
        return state
        
    total_cost = shares * price
    if total_cost > state["cash"]:
        print(f"Error: Insufficient funds. Total cost ${total_cost:,.2f} exceeds cash balance ${state['cash']:,.2f}.")
        return state
        
    # Deduct cash
    state["cash"] -= total_cost
    
    # Update portfolio position
    portfolio = state["portfolio"]
    if ticker in portfolio:
        current_shares = portfolio[ticker]["shares"]
        current_avg_cost = portfolio[ticker]["avg_cost"]
        
        # Calculate new average cost
        new_shares = current_shares + shares
        new_avg_cost = ((current_shares * current_avg_cost) + total_cost) / new_shares
        
        portfolio[ticker]["shares"] = new_shares
        portfolio[ticker]["avg_cost"] = new_avg_cost
    else:
        portfolio[ticker] = {
            "shares": shares,
            "avg_cost": price
        }
        
    # Append to history
    state["history"].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "BUY",
        "ticker": ticker,
        "shares": shares,
        "price": price,
        "total": total_cost
    })
    
    save_state(state)
    print(f"Success: Bought {shares:.2f} shares of {ticker} at ${price:.2f} each. Cost: ${total_cost:,.2f}.")
    return state

def execute_sell(state, ticker, shares):
    """
    Executes a stock sell trade, updating cash, portfolio, and transaction history.
    """
    if shares <= 0:
        print("Error: Shares quantity must be greater than zero.")
        return state
        
    portfolio = state["portfolio"]
    if ticker not in portfolio or portfolio[ticker]["shares"] < shares:
        owned = portfolio[ticker]["shares"] if ticker in portfolio else 0.0
        print(f"Error: Insufficient shares. You own {owned:.2f} shares of {ticker}, but tried to sell {shares:.2f}.")
        return state
        
    price = fetch_price(ticker)
    if price is None:
        print(f"Error: Could not retrieve price for ticker '{ticker}'.")
        return state
        
    total_revenue = shares * price
    
    # Add cash
    state["cash"] += total_revenue
    
    # Deduct shares
    portfolio[ticker]["shares"] -= shares
    if portfolio[ticker]["shares"] == 0:
        del portfolio[ticker]
        
    # Append to history
    state["history"].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "SELL",
        "ticker": ticker,
        "shares": shares,
        "price": price,
        "total": total_revenue
    })
    
    save_state(state)
    print(f"Success: Sold {shares:.2f} shares of {ticker} at ${price:.2f} each. Revenue: ${total_revenue:,.2f}.")
    return state

def display_portfolio(state):
    """
    Calculates current market values and prints portfolio statistics.
    """
    portfolio = state["portfolio"]
    cash = state["cash"]
    
    if not portfolio:
        print(f"\nPortfolio has no holdings. Cash Balance: ${cash:,.2f}")
        return
        
    print("\n--- Portfolio Holdings ---")
    print(f"{'Ticker':<10} | {'Shares':<10} | {'Avg Cost':<12} | {'Current Price':<15} | {'Cost Basis':<12} | {'Market Value':<15} | {'P&L':<12} | {'P&L %':<10}")
    print("-" * 105)
    
    total_holdings_value = 0.0
    total_cost_basis = 0.0
    
    for ticker, data in portfolio.items():
        shares = data["shares"]
        avg_cost = data["avg_cost"]
        
        current_price = fetch_price(ticker)
        if current_price is None:
            current_price = avg_cost  # Fallback
            
        cost_basis = shares * avg_cost
        market_value = shares * current_price
        pl = market_value - cost_basis
        pl_percent = (pl / cost_basis) * 100 if cost_basis > 0 else 0.0
        
        total_cost_basis += cost_basis
        total_holdings_value += market_value
        
        print(f"{ticker:<10} | {shares:<10,.2f} | ${avg_cost:<11,.2f} | ${current_price:<14,.2f} | ${cost_basis:<11,.2f} | ${market_value:<14,.2f} | {pl:<+11,.2f} | {pl_percent:+.2f}%")
        
    print("-" * 105)
    print(f"Cash Balance:       ${cash:,.2f}")
    print(f"Holdings Value:     ${total_holdings_value:,.2f}")
    print(f"Total Net Worth:    ${(cash + total_holdings_value):,.2f}")
    print("-" * 105)

def display_history(state):
    """
    Prints transaction log history.
    """
    history = state["history"]
    if not history:
        print("\nNo transactions recorded yet.")
        return
        
    print("\n--- Transaction History Log ---")
    print(f"{'Date/Time':<20} | {'Action':<6} | {'Ticker':<8} | {'Shares':<10} | {'Price':<12} | {'Total':<15}")
    print("-" * 80)
    for txn in history:
        print(f"{txn['timestamp']:<20} | {txn['type']:<6} | {txn['ticker']:<8} | {txn['shares']:<10,.2f} | ${txn['price']:<11,.2f} | ${txn['total']:<14,.2f}")
    print("-" * 80)

def display_help():
    """
    Prints command line interface instructions.
    """
    print("\nAvailable Commands:")
    print("  help                      - Show these instructions.")
    print("  balance                   - View cash balance and holdings value summary.")
    print("  quote <ticker>            - Get the current price of a ticker (e.g. quote TSLA).")
    print("  buy <ticker> <quantity>   - Buy shares (e.g. buy AAPL 5).")
    print("  sell <ticker> <quantity>  - Sell shares (e.g. sell AAPL 3).")
    print("  portfolio                 - View detailed holdings and gain/loss percentages.")
    print("  history                   - View trade log history.")
    print("  exit                      - Save account progress and close terminal.")

def main():
    print("==================================================")
    print("          SIMULATED PAPER TRADING TERMINAL        ")
    print("        Type 'help' to see available commands     ")
    print("==================================================")
    
    state = load_state()
    display_help()
    
    while True:
        try:
            user_input = input("\npaper-trade> ").strip()
            if not user_input:
                continue
                
            parts = user_input.split()
            command = parts[0].lower()
            
            if command == "help":
                display_help()
            elif command == "balance":
                print(f"Cash Balance: ${state['cash']:,.2f}")
            elif command == "quote":
                if len(parts) < 2:
                    print("Usage: quote <ticker>")
                    continue
                ticker = parts[1].upper()
                price = fetch_price(ticker)
                if price is not None:
                    print(f"{ticker} Current Price: ${price:.2f}")
                else:
                    print(f"Error: Could not retrieve price for ticker '{ticker}'.")
            elif command == "buy":
                if len(parts) < 3:
                    print("Usage: buy <ticker> <quantity>")
                    continue
                ticker = parts[1].upper()
                try:
                    qty = float(parts[2])
                    state = execute_buy(state, ticker, qty)
                except ValueError:
                    print("Error: Quantity must be a number.")
            elif command == "sell":
                if len(parts) < 3:
                    print("Usage: sell <ticker> <quantity>")
                    continue
                ticker = parts[1].upper()
                try:
                    qty = float(parts[2])
                    state = execute_sell(state, ticker, qty)
                except ValueError:
                    print("Error: Quantity must be a number.")
            elif command == "portfolio":
                display_portfolio(state)
            elif command == "history":
                display_history(state)
            elif command == "exit":
                save_state(state)
                print("Account state saved. Exiting Paper Trading Terminal. Goodbye!")
                break
            else:
                print(f"Unknown command: '{command}'. Type 'help' for options.")
        except (KeyboardInterrupt, EOFError):
            save_state(state)
            print("\nExiting terminal session. Goodbye!")
            break

if __name__ == "__main__":
    main()
