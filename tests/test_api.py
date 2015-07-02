import json

from pilo.source import JsonSource
from pilo.fields import Dict, Form, Integer, List, String

from . import TestCase


class Item(Form):

    id = String()
    href = String()
    reservations = String()
    metadata = Dict(String(), String())
    tags = List(String())
    capacity = Integer()
    available = Integer()
    committed = Integer()


class Reservation(Form):

    id = String()
    href = String()
    reservations = String()
    metadata = Dict(String(), String())
    tags = List(String())
    capacity = Integer()
    available = Integer()
    committed = Integer()


class TestAPI(TestCase):

    def test_items(self):
        payload = {
          "metadata": {
            "name": "bday party",
            "ticket_class": "GA"
          },
          "tags": ["event"],
          "capacity": 10
        }
        create_response = self.client.post(
            '/items', data=json.dumps(payload), content_type='application/json'
        )
        self.assertEqual(create_response.status_code, 201)
        item = Item(JsonSource(create_response.data))

        index_response = self.client.get(
            '/items', content_type='application/json'
        )
        self.assertEqual(index_response.status_code, 200)
        items = [Item(x) for x in JsonSource(index_response.data).data]

        self.assertEqual(items[0], item)

        show_response = self.client.get(
            '/items/{}'.format(item.id), content_type='application/json'
        )
        self.assertEqual(show_response.status_code, 200)
        self.assertEqual(Item(JsonSource(show_response.data)), item)


    def test_reservations(self):
        pass
