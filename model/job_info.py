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
