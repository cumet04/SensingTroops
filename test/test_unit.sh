#!/bin/bash

rec_port=53000
rec_ep="http://localhost:$rec_port/recruiter"
com_port=52000
com_ep="http://localhost:$com_port/commander"

cd $(dirname "${0}")
cd ..
kill_list=()

python troops/recruiter.py $rec_port &
kill_list+=($!)
jasmine-node test/spec/recruiter_unit_spec.js --config ep=rec_ep

python troops/commander.py $com_port &
kill_list+=($!)
jasmine-node test/spec/commander_unit_spec.js --config ep=com_ep

echo ${kill_list[@]} | xargs kill >/dev/null

# pvt_port=50000
# sgt_port=51000
# cpt_port=52000
# 
# 
# cd $(dirname "${0}")
# cd ../troops
# kill_list=()
# 
# python captain.py $cpt_port &
# kill_list+=($!)
# sleep 0.2
# python sergeant.py $sgt_port localhost $cpt_port &
# kill_list+=($!)
# sleep 0.2
# python private.py $pvt_port localhost $sgt_port &
# kill_list+=($!)
# sleep 0.5
# 
# cd ../test
# jasmine-node .
# echo ${kill_list[@]} | xargs kill >/dev/null
