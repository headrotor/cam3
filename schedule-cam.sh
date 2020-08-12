#!/bin/bash
# run this at 3PM: crontab -e
# 0 4 * * * /home/pi/gith/camscript-py3/schedule-cam.sh   >> ~/cronlog.txt 2>&1


# run scheduler to start and stop timelapse
cd /home/pi/camscript
python3 sun-chron.py
