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
from astral import SunDirection
import astral
import subprocess



if __name__ == '__main__':


    city_name = "San Francisco"


    #a.solar_depression = 'nautical'
    # degrees below horizon, so exactly at sunset
    #sun.solar_depression = 0.0
    sun.solar_depression = 'civil'

    city = LocationInfo(city_name)

    print('Information for %s/%s\n' % (city_name, city.region))

    s  = sun(city.observer,
             date=datetime.date.today())
#             dawn_dusk_depression=sun.solar_depression)



    # begin and end time of golden hour
    beg, end = astral.sun.golden_hour(city.observer,
                                      datetime.date.today(),
                                      SunDirection.SETTING,
                                      city.tzinfo)


    # at defaults to tomorrow
    #print('Sunset:  {} {}' % sun[sunset].hour, sun.minute)
    
    # start 1 hour before sunset
    start_time =  s['sunset'] + datetime.timedelta(hours = -1)

    # stop end end of golden hour (when sun is 4 degrees below horizon)
    stop_time = end


    print('  Sunset:  %s' % str(s['sunset']))
    print(' G begin:  %s' % str(beg))
    print('Gold end:  %s' % str(end))
    print('   Start:  %s' % str(start_time))
    print('    Stop:  %s' % str(stop_time))


    
    start_cmd = ['at', '-f', '/home/pi/camscript/start-lapse.sh']
    start_cmd.append('{:02d}:{:02d}'.format(start_time.hour,start_time.minute))
    print(" ".join(start_cmd))
    subprocess.run(start_cmd)

    stop_cmd = ['at', '-f', '/home/pi/camscript/stop-lapse.sh']
    stop_cmd.append('{:02d}:{:02d}'.format(stop_time.hour,stop_time.minute))
    print(" ".join(stop_cmd))
    subprocess.run(stop_cmd)
