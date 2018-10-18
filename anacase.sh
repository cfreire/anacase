#!/usr/bin/env bash

# anacase run script
# 20180724 Cesar Freire

echo 'sync github version'
git checkout master
git reset --hard HEAD~
git pull
echo 'starting anacase...'
/usr/bin/python3 anacase.py
