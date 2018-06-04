#!/bin/bash

# anacase run script
# 20180604 Cesar Freire

DIRECTORY='anacase'
REPO='https://github.com/cfreire/anacase.git'

if [ ! -d "$DIRECTORY" ]; then
	echo 'clonning anacase from ' "$REPO"
	git clone "$REPO"
fi
	cd $DIRECTORY
	echo 'sync github version'
	git pull
	echo 'startting anacase...'
	./anacase.py

