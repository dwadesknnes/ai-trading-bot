import os
from dataclasses import dataclass

@dataclass
class Settings:
    MODE: str = os.getenv("MODE", "paper")
    MAX_DAILY_DRAWDOWN: float = float(os.getenv("MAX_DAILY_DRAWDOWN", 0.05))
    MAX_PER_TRADE_RISK: float = float(os.getenv("MAX_PER_TRADE_RISK", 0.01))
    MAX_PER_ASSET_EXPOSURE: float = float(os.getenv("MAX_PER_ASSET_EXPOSURE", 0.20))
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID")

SETTINGS = Settings()
