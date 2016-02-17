#!/bin/bash

cd ..
python captain.py 52000 &
sleep 0.2
python sergeant.py 51000 localhost 52000 &
sleep 0.2
python private.py 50000 localhost 51000 &

cd test
jasmine-node .
pkill python
