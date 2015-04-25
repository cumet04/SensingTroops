#!/bin/bash

sergeant=$SERGEANT

if [ ! -e ./config ];then
    curl http://$sergeant/sergeant.sh?config > ./config
fi

interval=$(cat ./config)
if [[ $interval =~ stop ]];then exit 0;fi

curl http://$sergeant/sergeant.sh?set=aaa

sleep $interval
if [ $? -ne 0 ];then exit -1;fi
exec sh ./push_value.sh
