#!/usr/bin/env python
import ADC0832
import time
import math
import os
import sys
import paho.mqtt.client as mqtt
import json

THINGSBOARD_HOST = '4.206.153.143'
ACCESS_TOKEN = 'ovR0JQlLORzqH21UpgfT'

# Data capture and upload interval in seconds. Less interval will eventually hang the DHT22.
INTERVAL=2

sensor_data = {'celsius': 0, 'fahrenheit': 0}

next_reading = time.time() 

client = mqtt.Client()

# Set access token
client.username_pw_set(ACCESS_TOKEN)

# Connect to ThingsBoard using default MQTT port and 60 seconds keepalive interval
client.connect(THINGSBOARD_HOST, 1883, 60)

client.loop_start()

def init():
  ADC0832.setup()

def loop():
  global next_reading
  while True:
    res = ADC0832.getADC(0)
    Vr = 3.3 * float(res) / 255
    Rt = 10000 * Vr / (3.3 - Vr)
    temp = 1/(((math.log(Rt / 10000)) / 3380) + (1 / (273.15+25)))
    Cel = temp - 273.15
    Fah = Cel * 1.8 + 32
    print ('Celsius: %.2f C  Fahrenheit: %.2f F' % (Cel, Fah))
    
    sensor_data['celsius'] = Cel
    sensor_data['fahrenheit'] = Fah
    
    # Sending humidity and temperature data to ThingsBoard
    client.publish('v1/devices/me/telemetry', json.dumps(sensor_data), 1)

    next_reading += INTERVAL
    sleep_time = next_reading-time.time()
    if sleep_time > 0:
        time.sleep(sleep_time)

if __name__ == '__main__':
    init()
    try:
        loop()
    except KeyboardInterrupt: 
        ADC0832.destroy()
        print ('The end !')

client.loop_stop()
client.disconnect()
