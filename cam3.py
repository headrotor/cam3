#!/usr/bin/python3

# this is Python 3!

import sys
import os
import time
import select
import subprocess
import serial
import termios
import datetime

# requirements: Canon camera with CHDK installed and bootable
# https://chdk.fandom.com/wiki/CHDK

# install chdk ptp from here: https://app.assembla.com/wiki/show/chdkptp

#### Local defs

# serial port for FIT indicator RGB LED. "None" to disable
#blinkyport = "/dev/ttyACM0"
# Keeps hanging so f it
blinkyport = None

# path to your chdkptp installation, including lua stuff
chdkptp_path = "/home/pi/camscript/chdkptp-r921/"

# path to the root of directory to store jpgs for timelapse processing.
# a subdirectory is created with the current date and images are moved there
# with sequential numbers for ffmpeg timelapse generation
img_root = "/home/pi/cam/jpg"

# check for the existence of this file. When it's deleted stop
# the capture loop. This is how the movie generation process stops
# the image generation process
semaphore_fn = "/home/pi/cam/running.txt"

#Reset hub
# sudo ./usbreset /dev/bus/usb/008/004


class Blinky(object):
    # for setting FIT indicator led
    # Use None as serial port string to disable
    def __init__(self, serport=None, write_timeout=0.1):
        if serport is None:
            self.ser = None
            return
        self.ser = serial.Serial(serport, timeout=write_timeout)  # open serial port

    def setc(self,colorstr):
        #self.ser.write(bytes(colorstr,'utf-8'))
        if self.ser is None:
            return
        try:
            self.ser.write(colorstr)
            self.ser.flush()
        except termios.error:
            print("Blinky termios error")
        except serial.SerialException:
            print("Blinky serial exception")

# class for indicator LED
led = Blinky(serport=blinkyport)
#led = Blinky(serport=None)


# tell chdkptp where to find its lua stuff
# should use os.path.join() but this works
os.putenv("LUA_PATH",  chdkptp_path + "lua/?.lua;;")
os.putenv("LUA_CPATH", chdkptp_path + "?.so;;")

p = subprocess.Popen([chdkptp_path + "chdkptp"],
                     shell=True,
                     stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)
#                     bufsize=1)
#                     universal_newlines=True)

def send_chdkptp(p, cmd, pause=0.1, verb=True):
    """" send a command to chdk ptp and read response via stdout.
    TODO: check stderr"""
    
    p.stdin.write(cmd + b"\n") 
    p.stdin.flush()

    time.sleep(pause)
    y=select.poll()
    y.register(p.stdout,select.POLLIN)


    result = []

    while True:
        if y.poll(1):
            line = p.stdout.readline() 
            if verb:
                print('got "' + line.decode("utf-8") + '"')
            if len(line) > 0:
                result.append(line.decode("utf-8"))
            else:
                return result
            #y.register(p.stdout,select.POLLIN)
            time.sleep(pause)
        else:
            #print("done")
            #sys.stdout.flush()
            return result



error_detected = False

#sudo usbreset "fit_StatUSB"

led.setc(b"F10\n")
led.setc(b"#FF00FF\n")

# connect to camera.
result = send_chdkptp(p, b"c\n", pause=1.0)
led.setc(b"#FF00FF\n")

print("Got connection result: " + str(result))
sys.stdout.flush()

# test this for connection

# set to record mode. Will error if already in rec mode but shruggie. 
send_chdkptp(p, b"rec\n")



send_chdkptp(p, b"=set_backlight(1)\n") 

# set capture mode P
#https://chdk.fandom.com/wiki/Script_commands#set_capture_mode.28modenum.29
send_chdkptp(p, b"=set_capture_mode(2)\n")

# set M2 image resolution
send_chdkptp(p, b'=props=require("propcase") set_prop(props.RESOLUTION, 3)\n')

# set normal (not superfine) image quality
send_chdkptp(p, b'=props=require("propcase") set_prop(props.QUALITY, 1)\n')

# turn off autofocus and focus at infinity
send_chdkptp(p, b"=set_mf(1)\n") 
send_chdkptp(p, b"=set_aflock(1)\n") 
send_chdkptp(p, b"=set_focus(30000)\n") 

# set zoom
send_chdkptp(p, b"=set_zoom(20)\n")


# turn off stabilization
#send_chdkptp(p, b"=set_aflock(1)\n") 
p.stdin.flush()


# set camera in P mode. otherwise slow...
#=capmode=require("capmode") return capmode.get_name()
# shoudl return P

# todo: use =return get_live_histo() to get histogram, set iso/exposure based on that? Needs M mode?
# set clock    set_clock(year, month, day, hour, minute, second) 

imlist  = []



# make destination directory based on date....
datestr = time.strftime('%2y-%3j') #year followed by day in year
daystr =  time.strftime('%2y-%2m-%d') #year followed by  mo, day

dest_path = os.path.join(img_root, datestr)

if not os.path.exists(dest_path):
    print("creating jpg dir " + dest_path)
    os.mkdir(dest_path)

# make semaphore file
open(semaphore_fn, 'a').close()
time.sleep(1)
print("loop started at" + str(datetime.datetime.now()))

imcount = 0
loopcount = 0
# run forever and wait to be killed by cronjob.
# a cleaner way is to trap a "kill -15" signal or semaphore...
while os.path.exists(semaphore_fn):

    sys.stdout.flush()
    if error_detected:
        led.setc(b"#FF0000\n")
    else:
        led.setc(b"#00FF00\n")

    res = send_chdkptp(p, b"shoot -dl\n",pause=1.0)

    led.setc(b"#0000FF\n")
    # loop through all returned lines, look for image names

    for line in res:
        if "JPG" in line:
            img_fields  = line.split('>')
            if len(img_fields) > 1:
                # did we get a valid image name?
                mv_cmd = ["mv", '-f']
                # source file
                mv_cmd.append( img_fields[1].strip())
                # destination path
                mv_cmd.append(os.path.join(dest_path, "img_{:05}.jpg".format(imcount)))
                
                #mvstr = "mv {0} {1}/{0}".format(img_fields[1].strip(), dest_path) 
                print(" ".join(mv_cmd)) 

                # mv downloaded image to new place:
                result = subprocess.run(mv_cmd, capture_output=True)
                #p#rint("mv stdout: " + str(result.stdout))
                if len(result.stderr) > 0:
                    # handle errors here. disk full?
                    print("mv stderr: " + str(result.stderr))
                    error_detected = True
                imcount +=1
                result = send_chdkptp(p, b"imrm\n", 1.0)
                print(str(result))
                
                sys.stdout.flush()

        else:
            #print("Invalid image name? " + line) 
            pass

    loopcount += 1
    
    if (loopcount > imcount + 10):
        # not getting images for some reason
        error_detected = True

# ok here we are done with the loop. Turn off the backlight.
print("loop terminated at" + str(datetime.datetime.now()))

# wait for last download to finish
time.sleep(10)

# delete ALL existing images on SD card so we con't fill it up (careful!)
result = send_chdkptp(p, b"imrm\n", 1.0)
#print(str(result))


time.sleep(600)

result = send_chdkptp(p, b"imrm\n", 1.0)
#print(str(result))
sys.stdout.flush()

# turn off backlight to finish
result = send_chdkptp(p, b"=set_backlight(0)\n") 
print(str(result))

result = send_chdkptp(p, b"quit\n") 
print(str(result))


print("job finished at" + str(datetime.datetime.now()))
sys.stdout.flush()

exit()
