import argparse
import signal
from model import Soldier

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'id', metavar='id', type=str, help='Target id of app')
    parser.add_argument(
        'name', metavar='name', type=str, help='Target name of app')
    parser.add_argument(
        '-R', '--rec_addr', type=str, help="recruiter url",
        default="http://localhost:50000/recruiter/")
    params = parser.parse_args()

    soldier = Soldier(params.id, params.name)
    soldier.awake(params.rec_addr, 1)

    # 強制終了のハンドラ
    original_shutdown = signal.getsignal(signal.SIGINT)
    def shutdown(signum, frame):
        soldier.__del__()
        original_shutdown(signum, frame)
    signal.signal(signal.SIGINT, shutdown)

    while True:
        try:
            pass
        except KeyboardInterrupt:
            break
