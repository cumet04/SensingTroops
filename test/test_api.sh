#!/bin/bash

cd ..
python3 captain.py 52000 &
sleep 0.2
python3 sergeant.py 51000 localhost 52000 &
sleep 0.2
python3 private.py 50000 localhost 51000 &

cd test
jasmine-node .
pkill python3
