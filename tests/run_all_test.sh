#!/bin/bash

cwd=`dirname "${0}"`
expr "${0}" : "/.*" > /dev/null || cwd=`(cd "${cwd}" && pwd)`
cd $cwd/..

source venv/bin/activate
echo -e "\n>> test recruiter unit" && python -m tests.recruiter_test && \
echo -e "\n>> test commander unit" && python -m tests.commander_test && \
echo -e "\n>> test leader unit" && python -m tests.leader_test && \
echo -e "\n>> test soldier unit" && python -m tests.soldier_test && \
echo -e "\n>> test integration" && python -m tests.integration_test
