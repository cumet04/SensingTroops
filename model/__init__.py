import model.actor_info
import model.job_info
from model.actor_info import CommanderInfo, LeaderInfo, SoldierInfo
from model.job_info import Campaign, Mission, Order, Report, Work

_name = 'ResponseStatus'
_info = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'msg': {'type': 'string'}
    }
}
definitions = {}
definitions[_name] = _info
definitions.update(model.actor_info.definitions)
definitions.update(model.job_info.definitions)
