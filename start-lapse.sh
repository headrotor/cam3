#!/bin/bash

# kill it if we are running, ignoring errors if not
pkill -f cam3.py

# start it up for sure
cd /home/pi/camscript
python3 cam3.py  > cam-log.txt 2>&1


