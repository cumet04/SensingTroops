#/bin/bash

pvt_port=50000
sgt_port=51000
cpt_port=52000

cd $(dirname "${0}")
cd ..

mkdir work_tmp 2>/dev/null
rsync -a --delete troops work_tmp
rsync -a --delete test work_tmp

function dockerrun() {
    local id=$(docker run -d --expose 50000-53000 -v $PWD/work_tmp:/opt/app/ medalhkr/troops $@)
    local addr=$(docker inspect -f "{{ .NetworkSettings.IPAddress }}" $id)
    sleep 0.3
    echo $addr
}

cpt_addr=$(dockerrun python troops/captain.py $cpt_port)
sgt_addr=$(dockerrun python troops/sergeant.py $sgt_port $cpt_addr $cpt_port)
pvt_addr=$(dockerrun python troops/private.py $pvt_port $sgt_addr $sgt_port)
