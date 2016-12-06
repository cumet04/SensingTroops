from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

from model.info_obj import Requirement, Campaign, Mission, Order, Report, Work
from model.soldier import Soldier, SoldierInfo
from model.leader import Leader, LeaderInfo
from model.commander import Commander, CommanderInfo
from model.recruiter import Recruiter

definitions = dict()


def __init__():
    import model.soldier
    import model.leader
    import model.commander
    global definitions

    definitions["ResponseStatus"] = {
        'type': 'object',
        'properties': {
            'success': {'type': 'boolean'},
            'msg': {'type': 'string'}
        }
    }

    definitions["SoldierInfo"] = model.soldier.definition
    definitions["LeaderInfo"] = model.leader.definition
    definitions["CommanderInfo"] = model.commander.definition

    definitions.update(model.info_obj.definitions)

__init__()
