#!/bin/bash

cwd=`dirname "${0}"`
expr "${0}" : "/.*" > /dev/null || cwd=`(cd "${cwd}" && pwd)`
cd $cwd/..

source venv/bin/activate
python -m tests.recruiter_test
python -m tests.commander_test
python -m tests.leader_test
