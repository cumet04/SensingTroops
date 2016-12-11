#!/bin/bash

python troops/recruiter.py > /tmp/recruiter.log &
sleep 0.1
python troops/commander.py --port 51000 > /tmp/commander_00.log &
python troops/commander.py --port 51001 > /tmp/commander_01.log &
sleep 0.1

for i in $(seq 52000 52005)
do
    python troops/leader.py --port $i > /tmp/leader_${i:3:2}.log &
done

sleep 0.1

for i in $(seq 53000 53011)
do
    python troops/soldier.py --port $i > /tmp/soldier_${i:3:2}.log &
done
