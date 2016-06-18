#!/bin/bash

cwd=`dirname "${0}"`
expr "${0}" : "/.*" > /dev/null || cwd=`(cd "${cwd}" && pwd)`
cd $cwd/..

source venv/bin/activate
echo ">> test recruiter unit"; python -m tests.recruiter_test && \
echo ">> test commander unit"; python -m tests.commander_test && \
echo ">> test leader unit"; python -m tests.leader_test && \
echo ">> test integration"; python -m tests.integration_test
