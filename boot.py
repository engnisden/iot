# boot.py -- run on boot-up
import network, time
from machine import Pin

greenLed = Pin(2, Pin.OUT)
yellowLed = Pin(3, Pin.OUT)
redLed = Pin(4, Pin.OUT)

nice_time = 0.1 #time between blinks

SSID = ""
SSID_PASSWORD = ""

def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(SSID, SSID_PASSWORD)
        while not sta_if.isconnected():
            greenLed.toggle()
            time.sleep(0.1)
            yellowLed.toggle()
            time.sleep(0.1)
            redLed.toggle()
            time.sleep(0.1)
 
            greenLed.toggle()
            time.sleep(0.1)
            yellowLed.toggle()
            time.sleep(0.1)
            redLed.toggle()
            time.sleep(0.1)
            time.sleep(1)
    print('Connected! Network config:', sta_if.ifconfig())
    
print("Connecting to your wifi...")
do_connect()
