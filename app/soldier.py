import argparse
from utils.recruiter_client import RecruiterClient
from model.soldier import Soldier

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'id', metavar='id', type=str, help='Target id of app')
    parser.add_argument(
        'name', metavar='name', type=str, help='Target name of app')
    params = parser.parse_args()

    soldier = Soldier(params.id, params.name)
    rec_client = RecruiterClient.gen_rest_client(
        'http://localhost:50000/recruiter/')
    soldier.awake(rec_client, 1)
