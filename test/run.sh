#!/bin/bash

cd ..
pvt_port=50000
python3 captain.py 52000 &
sleep 0.5
for sgt_port in $(seq 51000 51003);do
    python3 sergeant.py $sgt_port localhost 52000 &
    sleep 0.5
    for i in $(seq 0 4);do
        python3 private.py $pvt_port localhost $sgt_port &
        pvt_port=$((pvt_port+1))
    done
done
