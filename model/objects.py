from collections import namedtuple


def _to_list(info):
    return list(info['properties'].keys())


definitions = {}

_name = 'ResponseStatus'
_info = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'msg': {'type': 'string'}
    }
}
definitions[_name] = _info


_name = 'SoldierInfo'
_info = {
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
definitions[_name] = _info
SoldierInfo = namedtuple(_name, _to_list(_info))

_name = 'LeaderInfo'
_info = {
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
definitions[_name] = _info
LeaderInfo = namedtuple(_name, _to_list(_info))

_name = 'CommanderInfo'
_info = {
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
definitions[_name] = _info
CommanderInfo = namedtuple(_name, _to_list(_info))

_name = 'Campaign'
_info = {
    'type': 'object',
    'properties': {
        'author': {'type': 'string'},
        'requirements': {'type': 'string'},
        'trigger': {'type': 'string'},
        'place': {'type': 'string'},
        'purpose': {'type': 'string'},
        'destination': {'type': 'string'}
    }
}
definitions[_name] = _info
Campaign = namedtuple(_name, _to_list(_info))

_name = 'Mission'
_info = {
    'type': 'object',
    'properties': {
        'author': {'type': 'string'},
        'requirements': {'type': 'string'},
        'trigger': {'type': 'string'},
        'place': {'type': 'string'},
        'purpose': {'type': 'string'},
        'destination': {'type': 'string'}
    }
}
definitions[_name] = _info
Mission = namedtuple(_name, _to_list(_info))

_name = 'Order'
_info = {
    'type': 'object',
    'properties': {
        'author': {'type': 'string'},
        'requirements': {'type': 'string'},
        'trigger': {'type': 'string'},
        'place': {'type': 'string'},
        'purpose': {'type': 'string'},
        'destination': {'type': 'string'}
    }
}
definitions[_name] = _info
Order = namedtuple(_name, _to_list(_info))

_name = 'Report'
_info = {
    'type': 'object',
    'properties': {
        'time': {'type': 'string'},
        'purpose': {'type': 'string'},
        'values': {'type': 'string'}
    }
}
definitions[_name] = _info
Report = namedtuple(_name, _to_list(_info))

_name = 'Work'
_info = {
    'type': 'object',
    'properties': {
        'time': {'type': 'string'},
        'purpose': {'type': 'string'},
        'values': {'type': 'string'}
    }
}
definitions[_name] = _info
Work = namedtuple(_name, _to_list(_info))
