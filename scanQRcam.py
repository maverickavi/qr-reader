#!/usr/bin/python
from sys import argv
import zbar
from RPi import GPIO
from RPLCD.gpio import CharLCD
from firebase import Firebase
from time import localtime, strftime
import psutil
import time
import os

#create LCD instance
lcd = CharLCD(pin_rs=15, pin_rw=18, pin_e=16, pins_data=[21, 22, 23, 24], numbering_mode=GPIO.BOARD, cols = 16, rows = 2)

# create a Processor
proc = zbar.Processor()

# configure the Processor
proc.parse_config('enable')

# initialize the Processor
device = '/dev/video0'
if len(argv) > 1:
    device = argv[1]
proc.init(device,enable_display=False)

lcd.clear()
lcd.write_string("SCANNING...")

#instantiate firebase
f= Firebase('https://cmtou-raspi.firebaseio.com/participants')

#sync date and time
os.system('''sudo date -s "$(wget -qSO- --max-redirect=0 google.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z"''')

# setup a callback
def my_handler(proc, image, closure):
    # extract results
    for symbol in image.symbols:
	lcd.clear()
#	lcd.write_string("Welcome")
#	lcd.set_cursor(0,1)
	lcd.write_string(symbol.data)
	if symbol.data == "shutdown":
		time.sleep(5)
		lcd.clear()
		os.system("sudo shutdown -h now")
	try:
		r = f.push({'QR Code': symbol.data , 'time': strftime("%Y-%m-%d %H:%M:%S", localtime())})
		print r
		time.sleep(1)		
	except:
		print "connection failed"

	lcd.clear()
	lcd.write_string("SCANNING...")

proc.set_data_handler(my_handler)

# enable the preview window
proc.visible = False

# initiate scanning
proc.active = True

try:
    # keep scanning until user provides key/mouse input
    proc.user_wait()
except zbar.WindowClosed, e:
    pass
