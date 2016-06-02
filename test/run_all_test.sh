#!/bin/bash

cwd=`dirname "${0}"`
expr "${0}" : "/.*" > /dev/null || cwd=`(cd "${cwd}" && pwd)`
cd $cwd

source ../venv/bin/activate
PYTHONPATH=".." python -m unittest *.py
