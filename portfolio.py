# portfolio.py
# Tracks current holdings, value, and exposures

class Portfolio:
    def __init__(self, capital=0):
        self.capital = capital
        self.positions = {}  # {ticker: {"qty": int, "avg_price": float}}
        self.equity_curve = [capital]  # Track equity over time

    def update(self, ticker, qty, price):
        pos = self.positions.get(ticker, {"qty": 0, "avg_price": 0})
        total_qty = pos["qty"] + qty
        if total_qty == 0:
            self.positions.pop(ticker, None)
        else:
            avg_price = (
                (pos["qty"] * pos["avg_price"] + qty * price) / total_qty
                if total_qty != 0 else 0
            )
            self.positions[ticker] = {"qty": total_qty, "avg_price": avg_price}

    def get_value(self, price_dict):
        # price_dict: {ticker: current_price}
        value = 0
        for ticker, pos in self.positions.items():
            value += pos["qty"] * price_dict.get(ticker, pos["avg_price"])
        return value

    def get_positions(self):
        return self.positions.copy()

    def allocate(self, ticker, position_size, price):
        # Allocates as much as possible given available capital
        total_cost = position_size * price
        if total_cost > self.capital:
            actual_size = int(self.capital // price)
        else:
            actual_size = position_size
        return actual_size

    def execute_trade(self, ticker, signal, price, qty):
        # Simulate buying or selling and update capital/positions
        if signal == "buy":
            cost = qty * price
            if cost > self.capital:
                print(f"Insufficient capital to execute BUY for {ticker}")
                return
            self.capital -= cost
            self.update(ticker, qty, price)
        elif signal == "sell":
            self.capital += qty * price
            self.update(ticker, -qty, price)
        else:
            print(f"Unknown trade signal: {signal}")
        # Track equity after each trade (BUG FIXED: no sum needed, just add float)
        self.equity_curve.append(self.capital + self.get_value({t: price for t in self.positions}))

    def plot_equity_curve(self):
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 5))
        plt.plot(self.equity_curve, marker="o")
        plt.title("Portfolio Equity Curve")
        plt.xlabel("Trade Number")
        plt.ylabel("Equity ($)")
        plt.grid(True)
        plt.show()

# --- Demo/Test ---
if __name__ == "__main__":
    pf = Portfolio()
    pf.update("AAPL", 10, 195)
    pf.update("AAPL", -5, 200)
    print(pf.get_positions())
    print("Portfolio value:", pf.get_value({"AAPL": 202}))
