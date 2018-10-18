#!/usr/bin/env bash

# anacase run script
# 20181018 Cesar Freire
cd ~/anacase:
echo 'sync github version'
git reset --hard HEAD~
git checkout master
git pull
echo 'starting anacase...'
/usr/bin/python3 anacase.py
