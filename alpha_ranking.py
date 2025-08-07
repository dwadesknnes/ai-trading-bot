import pandas as pd

def calc_asset_alpha(df_trades):
    """
    Calculates alpha (mean pnl / std pnl) for each ticker.
    Returns a sorted list of tickers by alpha descending.
    """
    if df_trades is None or df_trades.empty:
        return []
    grouped = df_trades.groupby("ticker")
    alpha_scores = {}
    for ticker, group in grouped:
        pnl = group["pnl"]
        mean_pnl = pnl.mean()
        std_pnl = pnl.std() if pnl.std() > 0 else 1
        alpha = mean_pnl / std_pnl
        alpha_scores[ticker] = alpha
    ranked = sorted(alpha_scores.items(), key=lambda x: x[1], reverse=True)
    return [t for t, a in ranked]