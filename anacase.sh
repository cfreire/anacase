#!/bin/bash

# anacase run script
# 20180604 Cesar Freire

REPO='https://github.com/cfreire/anacase.git'
cd ~/anacase
echo 'sync github version'
git pull
echo 'startting anacase...'
./anacase.py

