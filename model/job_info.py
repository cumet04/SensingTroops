# ここで定義されるオブジェクト群は，生成後にプロパティを変更されないことを
# 期待する．つまりnamedtupleとほぼ同じ特性である．
# が，actor_infoと同じように書きたいのでここも通常のclassとして定義する．

import hashlib
from typing import List, Dict
from model.info_obj import InformationObject

definitions = {}

definitions['Requirement'] = {
    'type': 'object',
    'properties': {
        'values': {'type': 'array', 'items': {'type': 'string'}},
        'trigger': {'type': 'object'},
    }
}
class Requirement(InformationObject):
    def __init__(self,
                 values: List[str],
                 trigger: Dict):
        self.values = values
        self.trigger = trigger

    @classmethod
    def make(cls, source: dict):
        try:
            return cls(
                source['values'],
                source['trigger'],
            )
        except KeyError:
            raise TypeError

definitions['Campaign'] = {
    'type': 'object',
    'properties': {
        'author': {'type': 'string'},
        'requirement': {'$ref': '#/definitions/Requirement'},
        'trigger': {'type': 'object'},
        'place': {'type': 'string'},
        'purpose': {'type': 'string'},
        'destination': {'type': 'string'}
    }
}
class Campaign(InformationObject):
    def __init__(self,
                 author: str,
                 requirement: Requirement,
                 trigger: Dict,
                 place: str,
                 purpose: str,
                 destination: str):
        self.author = author
        self.requirement = requirement
        self.trigger = trigger
        self.place = place
        self.purpose = purpose
        self.destination = destination

    def get_id(self):
        source = self.purpose + self.place
        m = hashlib.md5()
        m.update(str(source).encode())
        return m.hexdigest()

    @classmethod
    def make(cls, source: dict):
        try:
            return cls(
                source['author'],
                Requirement.make(source['requirement']),
                source['trigger'],
                source['place'],
                source['purpose'],
                source['destination'],
            )
        except KeyError:
            raise TypeError


definitions['Mission'] = {
    'type': 'object',
    'properties': {
        'author': {'type': 'string'},
        'requirement': {'$ref': '#/definitions/Requirement'},
        'trigger': {'type': 'object'},
        'place': {'type': 'string'},
        'purpose': {'type': 'string'},
    }
}
class Mission(InformationObject):
    def __init__(self,
                 author: str,
                 requirement: Requirement,
                 trigger: Dict,
                 place: str,
                 purpose: str):
        self.author = author
        self.requirement = requirement
        self.trigger = trigger
        self.place = place
        self.purpose = purpose

    def get_id(self):
        source = self.purpose + self.place
        m = hashlib.md5()
        m.update(str(source).encode())
        return m.hexdigest()

    @classmethod
    def make(cls, source: dict):
        try:
            return cls(
                source['author'],
                Requirement.make(source['requirement']),
                source['trigger'],
                source['place'],
                source['purpose'],
            )
        except KeyError:
            raise TypeError


definitions['Order'] = {
    'type': 'object',
    'properties': {
        'author': {'type': 'string'},
        'values': {'type': 'array', 'items': {'type': 'string'}},
        'trigger': {'type': 'object'},
        'purpose': {'type': 'string'},
    }
}
class Order(InformationObject):
    def __init__(self,
                 author: str,
                 values: List[str],
                 trigger: Dict,
                 purpose: str):
        self.author = author
        self.values = values
        self.trigger = trigger
        self.purpose = purpose

    @classmethod
    def make(cls, source: dict):
        try:
            return cls(
                source['author'],
                source['values'],
                source['trigger'],
                source['purpose'],
            )
        except KeyError:
            raise TypeError


definitions['Report'] = {
    'type': 'object',
    'properties': {
        'time': {'type': 'string'},
        'purpose': {'type': 'string'},
        'values': {'type': 'array', 'items': {'type': 'object'}},
    }
}
class Report(InformationObject):
    def __init__(self,
                 time: str,
                 purpose: str,
                 values: List[Dict]):
        self.time = time
        self.purpose = purpose
        self.values = values

    @classmethod
    def make(cls, source: dict):
        try:
            return cls(
                source['time'],
                source['purpose'],
                source['values'],
            )
        except KeyError:
            raise TypeError

definitions['Work'] = {
    'type': 'object',
    'properties': {
        'time': {'type': 'string'},
        'purpose': {'type': 'string'},
        'values': {'type': 'array', 'items': {'type': 'object'}},
    }
}
class Work(InformationObject):
    def __init__(self,
                 time: str,
                 purpose: str,
                 values: List[Dict]):
        self.time = time
        self.purpose = purpose
        self.values = values

    @classmethod
    def make(cls, source: dict):
        try:
            return cls(
                source['time'],
                source['purpose'],
                source['values'],
            )
        except KeyError:
            raise TypeError

