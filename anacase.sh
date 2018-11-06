#!/usr/bin/env bash

# anacase run script
# 20181106 Cesar Freire
cd ~/anacase/

# Para atualizar retirar os comentários da próximas linhas
###########################################################
# git checkout master
# sleep 1
# git reset --hard HEAD
# sleep 1
# git clean -xffd
# sleep 1
# git pull
# sleep 1
###########################################################
echo 'starting anacase...'
/usr/bin/python3 anacase.py
