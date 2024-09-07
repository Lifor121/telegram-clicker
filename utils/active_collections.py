from datetime import datetime
from tortoise.expressions import Q
from db.models import Collection  # Не забудьте импортировать модель Collection


async def get_active_collections():
    now = datetime.now()
    seasonal_collections = await Collection.filter(
        Q(type='seasonal') &
        (Q(active_from__lte=now) & Q(active_to__gte=now))
    ).all()
    event_collections = await Collection.filter(
        Q(type='event') &
        (Q(active_from__lte=now) & Q(active_to__gte=now))
    ).all()
    permanent_collections = await Collection.filter(type='permanent').all()
    return permanent_collections + seasonal_collections + event_collections