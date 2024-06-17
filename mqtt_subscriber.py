#!/usr/bin/python

# Steven Coutts - stevec@couttsnet.com
#
# 29/07/2020
# Script to subscribe to a few MQTT topics on Home Assistant
# Do stuff based on received messages.
# Beginnings of LCD control functionality.
#
# 02/04/2021
# Remove LCD stuff and change to control fan

import private as priv
import RPi.GPIO as GPIO
import logging
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from systemd.journal import JournalHandler
import socket

log = logging.getLogger('mqtt_alarm')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

GPIO.setmode(GPIO.BCM)
GPIO.setup(priv.pin, GPIO.OUT)

def on_connect(client, userdata, flags, rc):
  print(("Connected with result code {0}".format(str(rc))))
  state = GPIO.input(priv.pin)
  publish.single(priv.MQTT_TOPIC_FAN_STATUS_PREFIX, state, hostname=priv.MQTT_HOST, client_id='enclosure', auth={'username': priv.username, 'password': priv.password})
  client.subscribe(priv.MQTT_TOPIC_FAN_PREFIX)

def on_message(client, userdata, msg):
  print("Message received-> " + str(msg.topic) + " " + str(msg.payload))
  log.info("Message received-> " + str(msg.topic) + " " + str(msg.payload))
  if 'extractor' in msg.topic:
    if 'off' in str(msg.payload):
      GPIO.output(priv.pin, 0)
      publish.single(priv.MQTT_TOPIC_FAN_STATUS_PREFIX, '0', hostname=priv.MQTT_HOST, client_id='enclosure', auth={'username': priv.username, 'password': priv.password})
    elif 'on' in str(msg.payload):
      GPIO.output(priv.pin, 1)
      publish.single(priv.MQTT_TOPIC_FAN_STATUS_PREFIX, '1', hostname=priv.MQTT_HOST, client_id='enclosure', auth={'username': priv.username, 'password': priv.password})

def subscribe_topic():
  client = mqtt.Client()
  client.on_connect = on_connect
  client.on_message = on_message
  client.username_pw_set(username=priv.username, password=priv.password)
  client.connect(priv.MQTT_HOST, 1883)
  client.loop_forever()

try:
  subscribe_topic()
except KeyboardInterrupt:
  log.info("Stopping...")
finally:
  print("*** GPIO Cleanup ***")
  GPIO.cleanup()
