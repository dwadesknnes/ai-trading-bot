# portfolio.py
# Tracks current holdings, value, and exposures

class Portfolio:
    def __init__(self, capital=0):
        self.capital = capital
        self.positions = {}  # {ticker: {"qty": int, "avg_price": float}}

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

# --- Demo/Test ---
if __name__ == "__main__":
    pf = Portfolio()
    pf.update("AAPL", 10, 195)
    pf.update("AAPL", -5, 200)
    print(pf.get_positions())
    print("Portfolio value:", pf.get_value({"AAPL": 202}))
