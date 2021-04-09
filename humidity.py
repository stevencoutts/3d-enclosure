#!/usr/bin/python3
#
import private as priv
import time
import logging
from systemd.journal import JournalHandler
import paho.mqtt.publish as publish
import Adafruit_DHT

log = logging.getLogger('mqtt_alarm')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
state_topic = 'enclosure/temperature'
state_topic2 = 'enclosure/humidity'
delay = 5

while True:
    time.sleep(5)
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    if humidity is not None and temperature is not None:
        print("Temp={0:0.1f}*C  Humidity={1:0.1f}%".format(temperature, humidity))
        publish.single(state_topic, temperature, hostname=priv.MQTT_HOST, client_id='enclosure', auth={'username':priv.username, 'password':priv.password})
        log.info("Enclosure Temperature -> " + str(temperature))
        publish.single(state_topic2, humidity, hostname=priv.MQTT_HOST, client_id='enclosure', auth={'username':priv.username, 'password':priv.password})
        log.info("Enclosure Humidity -> " + str(humidity))
    else:
        print("Failed to retrieve data from humidity sensor")