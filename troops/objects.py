#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
class ResponseStatus():
    Success = {
        'success': True,
        'msg': "status is ok"
    }
    NotFound = {
        'success': False,
        'msg': 'resource not found'
    }
    Failed = {
        'success': False,
        'msg': 'action is failed'
    }
    NotImplemented = {
        'success': False,
        'msg': 'this function is not implemented yet'
    }
    @staticmethod
    def make_error(msg):
        return {
            'success': False,
            'msg': msg
        }


_name = 'SoldierInfo'
_info = {
    'type': 'object',
    'properties': {
        'id': {'description': "the man's ID",
               'type': 'string'},
        'name': {'type': 'string'},
        'endpoint': {'type': 'string'},
        'weapons': {},
        'orders': {}
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
        'subordinates': {},
        'missions': {}
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
        'subordinates': {},
        'campaigns': {}
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
