#!/usr/bin/python3
# python cron job to do things at sunrise and sunset using 'at'
# run daily from crontab, e.g.


# requirements:
# pip install astral
# sudo apt install at

import sys
import time
import datetime
from astral.sun import sun
from astral import LocationInfo
import astral
import subprocess



if __name__ == '__main__':


    city_name = "San Francisco"

    
    #a.solar_depression = 'civil'
    #a.solar_depression = 'nautical'
    # degrees below horizon, so exactly at sunset
    sun.solar_depression = 0.0

    city = LocationInfo(city_name)

    print('Information for %s/%s\n' % (city_name, city.region))

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    print("tomorrow is {} {} {}".format(tomorrow.year,
                                        tomorrow.month,
                                        tomorrow.day))
    y, m, d = tomorrow.year, tomorrow.month, tomorrow.day
    s  = sun(city.observer, date=datetime.date(y, m, d))

    # 1 hour before sunset
    start_time =  s['sunset'] + datetime.timedelta(hours = -1)
    # n min after sunset
    stop_time = s['sunset'] + datetime.timedelta(hours = 1)
    print('Sunset:  %s' % str(s['sunset']))
    print(' Start:  %s' % str(start_time))
    print('  Stop:  %s' % str(stop_time))


    # at defaults to tomorrow
    #print('Sunset:  {} {}' % sun[sunset].hour, sun.minute)
    
    start_cmd = ['at', '-f', '/home/pi/gith/camscript-py3/start-lapse.sh']
    start_cmd.append('{:02d}:{:02d}'.format(start_time.hour,start_time.minute))
    print(" ".join(start_cmd))
    subprocess.run(start_cmd)

    stop_cmd = ['at', '-f', '/home/pi/gith/camscript-py3/stop-lapse.sh']
    stop_cmd.append('{:02d}:{:02d}'.format(stop_time.hour,stop_time.minute))
    print(" ".join(stop_cmd))
    subprocess.run(stop_cmd)
