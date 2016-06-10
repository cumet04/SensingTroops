from model.info_obj import InformationObject

definitions = {}

definitions['Campaign'] = {
    'type': 'object',
    'properties': {
        'author': {'type': 'string'},
        'requirements': {'type': 'object'},
        'trigger': {'type': 'object'},
        'place': {'type': 'string'},
        'purpose': {'type': 'string'},
        'destination': {'type': 'string'}
    }
}
class Campaign(InformationObject):
    def __init__(self,
                 author: str,
                 requirements: object,
                 trigger: object,
                 place: str,
                 purpose: str,
                 destination: str):
        self.author = author
        self.requirements = requirements
        self.trigger = trigger
        self.place = place
        self.purpose = purpose
        self.destination = destination

    @classmethod
    def make(cls, source: dict):
        try:
            return cls(
                source['author'],
                source['requirements'],
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
        'requirements': {'type': 'object'},
        'trigger': {'type': 'object'},
        'place': {'type': 'string'},
        'purpose': {'type': 'string'},
        'destination': {'type': 'string'}
    }
}
class Mission(InformationObject):
    def __init__(self,
                 author: str,
                 requirements: object,
                 trigger: object,
                 place: str,
                 purpose: str,
                 destination: str):
        self.author = author
        self.requirements = requirements
        self.trigger = trigger
        self.place = place
        self.purpose = purpose
        self.destination = destination

    @classmethod
    def make(cls, source: dict):
        try:
            return cls(
                source['author'],
                source['requirements'],
                source['trigger'],
                source['place'],
                source['purpose'],
                source['destination'],
            )
        except KeyError:
            raise TypeError


definitions['Order'] = {
    'type': 'object',
    'properties': {
        'author': {'type': 'string'},
        'requirements': {'type': 'object'},
        'trigger': {'type': 'object'},
        'purpose': {'type': 'string'},
        'destination': {'type': 'string'}
    }
}
class Order(InformationObject):
    def __init__(self,
                 author: str,
                 requirements: object,
                 trigger: object,
                 purpose: str,
                 destination: str):
        self.author = author
        self.requirements = requirements
        self.trigger = trigger
        self.purpose = purpose
        self.destination = destination

    @classmethod
    def make(cls, source: dict):
        try:
            return cls(
                source['author'],
                source['requirements'],
                source['trigger'],
                source['purpose'],
                source['destination'],
            )
        except KeyError:
            raise TypeError


definitions['Report'] = {
    'type': 'object',
    'properties': {
        'time': {'type': 'string'},
        'purpose': {'type': 'string'},
        'values': {'type': 'string'}
    }
}
class Report(InformationObject):
    def __init__(self,
                 time: str,
                 purpose: str,
                 values: object):
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
        'values': {'type': 'string'}
    }
}
class Work(InformationObject):
    def __init__(self,
                 time: str,
                 purpose: str,
                 values: object):
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

