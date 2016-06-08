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
class Campaign(object):
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

    def to_dict(self):
        return {
            "author": self.author,
            "requirements": self.requirements,
            "trigger": self.trigger,
            "place": self.place,
            "purpose": self.purpose,
            "destination": self.destination
        }


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
class Mission(object):
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

    def to_dict(self):
        return {
            "author": self.author,
            "requirements": self.requirements,
            "trigger": self.trigger,
            "place": self.place,
            "purpose": self.purpose,
            "destination": self.destination
        }


definitions['Order'] = {
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
class Order(object):
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

    def to_dict(self):
        return {
            "author": self.author,
            "requirements": self.requirements,
            "trigger": self.trigger,
            "place": self.place,
            "purpose": self.purpose,
            "destination": self.destination
        }


definitions['Report'] = {
    'type': 'object',
    'properties': {
        'time': {'type': 'string'},
        'purpose': {'type': 'string'},
        'values': {'type': 'string'}
    }
}
class Report(object):
    def __init__(self,
                 time: str,
                 purpose: str,
                 values: object):
        self.time = time
        self.purpose = purpose
        self.values = values

    def to_dict(self):
        return {
            "time": self.time,
            "purpose": self.purpose,
            "values": self.values
        }


definitions['Work'] = {
    'type': 'object',
    'properties': {
        'time': {'type': 'string'},
        'purpose': {'type': 'string'},
        'values': {'type': 'string'}
    }
}
class Work(object):
    def __init__(self,
                 time: str,
                 purpose: str,
                 values: object):
        self.time = time
        self.purpose = purpose
        self.values = values

    def to_dict(self):
        return {
            "time": self.time,
            "purpose": self.purpose,
            "values": self.values
        }
