#!/usr/bin/env bash

# anacase run script
# 20181018 Cesar Freire
cd ~/anacase/
echo 'sync github version'
git reset --hard HEAD~
sleep 2
git checkout master
sleep 2
git pull
sleep 2
echo 'starting anacase...'
/usr/bin/python3 anacase.py
