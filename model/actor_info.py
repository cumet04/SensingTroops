from model.job_info import Campaign, Mission, Order
from model.info_obj import InformationObject
from typing import List

definitions = dict()


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


class SoldierInfo(InformationObject):
    def __init__(self,
                 id: str,
                 name: str,
                 weapons: List[object],
                 orders: List[Order]):
        self.id = id
        self.name = name
        self.weapons = weapons
        self.orders = orders

    @classmethod
    def make(cls, source: dict):
        try:
            return cls(
                source['id'],
                source['name'],
                source['weapons'],
                [Order.make(o) for o in source['orders']]
            )
        except KeyError:
            raise TypeError


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


class LeaderInfo(InformationObject):
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

    @classmethod
    def make(cls, source: dict):
        try:
            return cls(
                source['id'],
                source['name'],
                source['endpoint'],
                source['subordinates'],
                [Mission.make(m) for m in source['missions']]
            )
        except KeyError:
            raise TypeError


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


class CommanderInfo(InformationObject):
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

    @classmethod
    def make(cls, source: dict):
        try:
            return cls(
                source['id'],
                source['name'],
                source['endpoint'],
                source['subordinates'],
                [Campaign.make(c) for c in source['campaigns']]
            )
        except KeyError:
            raise TypeError
