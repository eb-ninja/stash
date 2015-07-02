import uuid

from kazoo.client import KazooClient


items = {}


class Item(object):

    @classmethod
    def create(cls, capacity, metadata, tags):
        guid = uuid.uuid4()
        committed = 0
        available = capacity
        item = dict(
            id=guid,
            available=available,
            capacity=capacity,
            committed=committed,
            metadata=metadata,
            tags=tags,
        )
        items[guid] = item
        return item

    @classmethod
    def index(cls):
        return items.values()

    @classmethod
    def get(cls, guid):
        return items.get(guid)


reservations = {}


class Reservation(object):

    @classmethod
    def create(cls, item_guid):
        guid = uuid.uuid4()
        reservation = dict(
            id=guid,
        )
        reservations[guid] = reservation
        return reservation

    @classmethod
    def index(cls):
        return reservations.values()

    @classmethod
    def get(cls, guid):
        return reservations.get(guid)
