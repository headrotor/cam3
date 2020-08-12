# cam3
Camera timelapse code using Python 3, chdkptp, and ffmpeg. 

Camera: Canon SX-620 remote control via PTP mode from CHDK
Host: Raspberry Pi

At midnight, run schedule-cam.sh via a crontab entry.
This schedules start-lapse.sh and stop-lapse.sh shell scripts.
start-lapse repeatedly captures images by running cam3.py
stop-lapse kills start-lapse and processess images to mp4 video using ffmpeg.

Requires CHDK from  https://chdk.fandom.com/wiki/CHDK
requires chdkptp from here: https://app.assembla.com/wiki/show/chdkptp

Also requires ffmpeg installed from the usual sources, and a FIT StatUSB LED indicator is optional. 


# Installing CHDK:

Remote control of Canon Point-and-shoot cameras. Since 2009 none of
them work with gphoto2, so use PTP mode and CHDK. To install CHDK, must
make bootable drive.

Determine firmware by dragging image to STICKS
http://www.zenoshrdlu.com/stick/stick.html
Download correct CHDK image from here:

Use LICKS to make bootable SD card. Don't forget 'copy all files'
Best luck with <8GB SD cards
http://www.zenoshrdlu.com/licks/licks.html

Test with CLI interface via chdkptp
https://app.assembla.com/spaces/chdkptp/wiki/CLI_Quickstart
https://tools.assembla.com/svn/chdkptp/trunk/USAGE.TXT


