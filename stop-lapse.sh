#!/bin/bash

# kill it if we are running
pkill -f cam3.py

# let it die
sleep 10


# start movie processing
cd /home/pi/camscript
python3 mov3.py  /home/pi/cam/jpg >> mov-log.txt 2>&1


# upload to youtube, twitter, ...
