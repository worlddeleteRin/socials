from socials.apps.bots_events.models import BotEvent, BotEventsSearch, GetBotEventsQuery
from socials.database.main_db import db_provider


def get_bot_events(query: GetBotEventsQuery) -> BotEventsSearch:
    (skip, limit) = (query.skip, query.limit)
    filters = query.collect_db_filters_query()

    print('filters are', filters)
    
    result_total = db_provider.bots_events_db.count_documents(filters)

    result = db_provider.bots_events_db.find(
        filters
    ).skip(skip).limit(limit)
    events = [BotEvent(**e) for e in result]

    return BotEventsSearch(
        events=events,
        total=result_total
    )
