#!/bin/bash

pvt_port=50000
sgt_port=51000
cpt_port=52000

cd $(dirname "${0}")
cd ../troops

python captain.py $cpt_port &
sleep 0.2
python sergeant.py $sgt_port localhost $cpt_port &
sleep 0.2
python private.py $pvt_port localhost $sgt_port &
