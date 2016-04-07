#!/usr/bin/python3
# -*- coding: utf-8 -*-

from collections import namedtuple


SoldierInfo = namedtuple('SoldierInfo', [
        'id',
        'name',
        'endpoint',
        'weapons',
        'orders'
    ])
LeaderInfo = namedtuple('LeaderInfo', [
        'id',
        'name',
        'endpoint',
        'subordinates',
        'missions'
    ])
CommanderInfo = namedtuple('CommanderInfo', [
        'id',
        'name',
        'endpoint',
        'subordinates',
        'campaigns'
    ])

Campaign = namedtuple('Campaign', [
        'author',
        'requirements',
        'trigger',
        'place',
        'purpose',
        'destination'
    ])

Mission = namedtuple('Mission', [
        'author',
        'requirements',
        'trigger',
        'place',
        'purpose',
        'destination'
    ])

Order = namedtuple('Order', [
        'author',
        'requirements',
        'trigger',
        'place',
        'purpose',
        'destination'
    ])

Report = namedtuple('Report', [
        'time',
        'purpose',
        'values'
    ])

Work = namedtuple('Work', [
    'time',
    'purpose',
    'value'
])

