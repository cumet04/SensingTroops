import argparse
import signal
from model import Soldier
from utils.helpers import get_mac

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-I', '--id', type=str, default='', help='Target id of app')
    parser.add_argument(
        '-N', '--name', type=str, default='', help='Target name of app')
    parser.add_argument(
        '-R', '--rec_addr', type=str, help="recruiter url",
        default="http://localhost:50000/recruiter/")
    params = parser.parse_args()

    if params.id == "":
        params.id = get_mac()
    if params.name == "":
        params.name = "soldier"

    soldier = Soldier(params.id, params.name)
    soldier.awake(params.rec_addr, 1)

    # 強制終了のハンドラ
    original_shutdown = signal.getsignal(signal.SIGINT)
    def shutdown(signum, frame):
        soldier.shutdown()
        original_shutdown(signum, frame)
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    while True:
        pass
