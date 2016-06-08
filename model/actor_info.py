from model.job_info import Campaign, Mission, Order
from typing import List

definitions = {}


definitions['SoldierInfo'] = {
    'type': 'object',
    'properties': {
        'id': {'description': "the man's ID",
               'type': 'string'},
        'name': {'type': 'string'},
        'weapons': {'description': "A list of weapon",
                    'type': 'array',
                    'items': {'type': 'object'}},
        'orders': {'type': 'array',
                   'items': {'$ref': '#/definitions/Order'}},
    }
}
class SoldierInfo(object):
    def __init__(self,
                 id: str,
                 name: str,
                 weapons: List[object],
                 orders: List[Order]):
        self.id = id
        self.name = name
        self.weapons = weapons
        self.orders = orders

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "weapons": sorted(self.weapons),
            "orders": sorted([o.to_dict() for o in self.orders])
        }


definitions['LeaderInfo'] = {
    'type': 'object',
    'properties': {
        'id': {'description': "the man's ID",
               'type': 'string'},
        'name': {'type': 'string'},
        'endpoint': {'type': 'string'},
        'subordinates': {'description': "A list of subordinates's ID",
                         'type': 'array',
                         'items': {'type': 'string'}},
        'missions': {'type': 'array',
                     'items': {'$ref': '#/definitions/Mission'}},
    }
}
class LeaderInfo(object):
    def __init__(self,
                 id: str,
                 name: str,
                 endpoint: str,
                 subordinates: List[str],
                 missions: List[Mission]):
        self.id = id
        self.name = name
        self.endpoint = endpoint
        self.subordinates = subordinates
        self.missions = missions

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "endpoint": self.endpoint,
            "subordinates": sorted(self.subordinates),
            "missions": sorted([m.to_dict() for m in self.missions])
        }


definitions['CommanderInfo'] = {
    'type': 'object',
    'properties': {
        'id': {'description': "the man's ID",
               'type': 'string'},
        'name': {'type': 'string'},
        'endpoint': {'type': 'string'},
        'subordinates': {'description': "A list of subordinates's ID",
                         'type': 'array',
                         'items': {'type': 'string'}},
        'campaigns': {'type': 'array',
                      'items': {'$ref': '#/definitions/Campaign'}},
    }
}
class CommanderInfo(object):
    def __init__(self,
                 id: str,
                 name: str,
                 endpoint: str,
                 subordinates: List[str],
                 campaigns: List[Campaign]):
        self.id = id
        self.name = name
        self.endpoint = endpoint
        self.subordinates = subordinates
        self.campaigns = campaigns

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "endpoint": self.endpoint,
            "subordinates": sorted(self.subordinates),
            "campaigns": sorted([c.to_dict() for c in self.campaigns])
        }
