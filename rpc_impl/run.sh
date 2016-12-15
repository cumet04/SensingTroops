#!/bin/bash

python -m troops.recruiter > /tmp/recruiter.log &
sleep 0.1
python -m troops.commander --port 51000 > /tmp/commander_00.log &
python -m troops.commander --port 51001 > /tmp/commander_01.log &
sleep 0.1

for i in $(seq 52000 52005)
do
    python -m troops.leader --port $i > /tmp/leader_${i:3:2}.log &
done

sleep 0.1

for i in $(seq 53000 53011)
do
    python -m troops.soldier --port $i > /tmp/soldier_${i:3:2}.log &
done

python -m viewer.viewer

pkill python
