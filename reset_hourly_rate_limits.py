import os
from socials.config import settings
#os.environ['env_mode'] = 'prod'
os.environ['env_mode'] = settings.env_mode
from socials.database.main_db import db_provider
from socials.apps.bots.models import BotDailyMetrics

def reset_hourly_rate_limits():
    empty_metrics = BotDailyMetrics()
    db_provider.bots_db.update_many(
        {},
        {"$set": {
            "hourly_metrics": empty_metrics.dict()
        }}
    )

if __name__ == "__main__":
    reset_hourly_rate_limits()
