#!/bin/bash

pvt_num=5
sgt_num=4
pvt_port=50000
sgt_port=51000
cpt_port=52000

cd $(dirname "${0}")
cd ../troops

python captain.py $cpt_port &
sleep 0.5
for sgtp in $(seq 0 $((sgt_num-1)));do
    python sergeant.py $sgt_port localhost $cpt_port &
    sleep 0.5
    for pvtp in $(seq 0 $((pvt_num-1)));do
        python private.py $pvt_port localhost $sgt_port &
        pvt_port=$((pvt_port+1))
    done
    sgt_port=$((sgt_port+1))
done
