#!/bin/bash

# delete semaphore file to stop image capture loop. 
rm -f /home/pi/cam/running.txt

# let it catch the signal and stop
sleep 20

# start movie processing
cd /home/pi/camscript
python3 mov3.py  /home/pi/cam/jpg > mov-log.txt 2>&1

# if for some reason camera script didn't die, kill it anyway. 
#sleep 3600
#pkill -f cam3.py

# upload to youtube, twitter, ...
