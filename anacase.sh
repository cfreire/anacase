#!/bin/bash

# anacase run script
# 20180603 Cesar Freire

DIRECTORY='anacase'
REPO='https://github.com/cfreire/anacase.git'

if [ ! -d "$DIRECTORY" ]; then
	echo 'clonning anacase from'  "$REPO"
	git clone "$REPO"
fi
	cd $DIRECTORY
	echo 'sync github version'
	git fetch
	echo 'startting anacase...'
	./anacase.py

