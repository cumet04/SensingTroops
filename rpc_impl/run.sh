#!/bin/bash

python -u -m troops.recruiter > /tmp/recruiter.log &
sleep 0.1
python -u -m troops.commander --port 51000 > /tmp/commander_00.log &
python -u -m troops.commander --port 51001 > /tmp/commander_01.log &
sleep 0.1

for i in $(seq 52000 52005)
do
    python -u -m troops.leader --port $i > /tmp/leader_${i:3:2}.log &
done

sleep 0.1

for i in $(seq 53000 53011)
do
    python -u -m troops.soldier_tag --port $i > /tmp/soldier_${i:3:2}.log &
done


# python -u -m troops.recruiter > /tmp/recruiter.log &
# sleep 0.1
# python -u -m troops.commander --port 51000 > /tmp/commander_00.log &
# sleep 0.1
# python -u -m troops.leader --port 52000 > /tmp/leader_00.log &
# sleep 0.1
# python -u -m troops.soldier --port 53000 > /tmp/soldier_00.log &

function add_mission() {
    sleep 2
    uri='http://localhost:50001/xmlrpc/exec?endpoint=http://localhost:51000&method=add_mission'
    uri=${uri}'&param0={"destination":"mongodb://localhost:27017/troops/test","place":"All","requirements":["zero","random"],"trigger":2,"purpose":"purp"}'
    curl -g $uri
}

add_mission &

python -u -m viewer.viewer

pkill python
