#!/usr/bin/python
import time
from BMP280 import BMP280
import SSD1306
import RPi.GPIO as GPIO

import urllib3
import json 

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from thread import start_new_thread

class Button:

    lastStaten = True
    pin = 0

    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN)
        self.lastState = GPIO.input(pin)

    def isButtonPressed(self):
        state = GPIO.input(self.pin)
        result = self.lastState and not state 
        self.lastState = state
        return result

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used

invertButton = Button(6)
standardButton = Button(16)

# Initialise the BMP280 and use STANDARD mode (default value)
bmp = BMP280()
# 128x32 display with hardware I2C:
disp = SSD1306.SSD1306_128_32(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# 255 is white
# 0 is black
foregroundColor = 255
backgroundColor = 0

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=backgroundColor)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = 1
top = padding
bottom = height-padding
left = padding
right = width - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 8)

metric = True

lastPost = 0

angle = 270

def UpdateConditions(temperature, pressure):
    global bmp 
    global metric
    global backgroundColor
    global foregroundColor
    global lastPost
    global angle

    # Draw a filled box to clear the image.
    draw.rectangle(((0,0),(width-1,height-1)), outline=None, fill=backgroundColor)
    
    if(metric):
        draw.text((left, top),       "Temperature: {:.2f} C".format(temperature) ,  font=font, fill=foregroundColor)
        draw.text((left, top+8),     "Pressure: {:.2f} hPa".format(pressure), font=font, fill=foregroundColor)
    else:
        draw.text((left, top),       "Temperature: {:.2f} F".format(temperature * 1.8 +32),  font=font, fill=foregroundColor)
        draw.text((left, top+8),     "Pressure: {:.3f} in Hg".format(pressure / 33.863886666667 ), font=font, fill=foregroundColor)

    draw.pieslice([left+2,top+20,left+10,top+28], -90, angle, fill=foregroundColor, outline=None)

    # Display image.
    disp.image(image)
    disp.display()

    now = time.time()
    if(now - lastPost > 300):
        start_new_thread(PostConditions, (temperature, pressure))
        lastPost = now

def PostConditions(temperature, pressure):
    try:
        url = 'https://weathercenter.table.core.windows.net/WeatherData?sv=2017-07-29&si=stationreport&tn=weatherdata&sig=RNIR82260mjMW9cn6%2BhrCsznn5VSRLHljjPV77ZYCY4%3D'
        
        values = {'PartitionKey': 'student-pizero',
            'RowKey': time.asctime(time.gmtime()),
            'temperature': temperature,
            'pressure': pressure }

        http = urllib3.PoolManager()

        encoded_data = json.dumps(values).encode('utf-8')
        r = http.request(
            'POST',
            url,
            body=encoded_data,
            headers={'Content-Type': 'application/json',
                    'Accept': 'application/json;odata=nometadata'})
        print("Updated cloud weather table")
    except:
        print("Caught exception uploading current weather conditions to Azure")

was = 0
while True:

    if(invertButton.isButtonPressed()):
        temp = foregroundColor
        foregroundColor = backgroundColor
        backgroundColor = temp

    if(standardButton.isButtonPressed()):
        metric = not metric

    now = time.time()
    if((angle >= 270) and ((now - was) >= 5)):
        angle = -90
        temperature = bmp.readTemperature()

        # Read the current barometric pressure level
        pressure = bmp.readPressure() / 100.0

        print ("Temperature: %.2f C" % temperature)
        print ("Pressure:    %.3f hPa or %.3f in Hg" % (pressure, (pressure / 33.863886666667)))
        #print "Altitude:    %.2f" % altitude
    else:
        angle += 360/40
        
    UpdateConditions(temperature, pressure)

    time.sleep(.1)
