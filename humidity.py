#!/usr/bin/python3
#
import private as priv
import time
import logging
from systemd.journal import JournalHandler
import paho.mqtt.publish as publish
import Adafruit_DHT

DHT_SENSOR = Adafruit_DHT.DHT22

log = logging.getLogger('mqtt_alarm')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

delay = 30

while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, priv.DHT_PIN)
    if humidity is not None and temperature is not None:
        print("Temp={0:0.1f}*C  Humidity={1:0.1f}%".format(temperature, humidity))
        publish.single(priv.MQTT_TOPIC_TEMP_PREFIX, temperature, hostname=priv.MQTT_HOST, client_id='enclosure', auth={'username':priv.username, 'password':priv.password})
        log.info("Enclosure Temperature -> " + str(round(temperature,1)))
        publish.single(priv.MQTT_TOPIC_HUMID_PREFIX, humidity, hostname=priv.MQTT_HOST, client_id='enclosure', auth={'username':priv.username, 'password':priv.password})
        log.info("Enclosure Humidity -> " + str(round(humidity,1)))
    else:
        print("Failed to retrieve data from humidity sensor")
    time.sleep(delay)