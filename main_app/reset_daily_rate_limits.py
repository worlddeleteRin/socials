from database.main_db import db_provider
from apps.bots.models import BotDailyMetrics

def reset_daily_rate_limits():
    empty_metrics = BotDailyMetrics()
    db_provider.bots_db.update_many(
        {},
        {"$set": {
            "daily_metrics": empty_metrics.dict()
        }}
    )

if __name__ == "__main__":
    reset_daily_rate_limits()