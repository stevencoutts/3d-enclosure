#!/usr/bin/python3
"""
Humidity and Temperature Monitoring Script
This script reads data from a DHT22 sensor and publishes it to MQTT.
"""

import os
import time
import logging
from dotenv import load_dotenv
from systemd.journal import JournalHandler
import paho.mqtt.publish as publish
import Adafruit_DHT

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger('mqtt_alarm')
logger.addHandler(JournalHandler())
logger.setLevel(logging.INFO)

# Constants
DHT_SENSOR = Adafruit_DHT.DHT22
DELAY = 30

def get_config() -> dict:
    """
    Get configuration from environment variables.
    
    Returns:
        dict: Configuration dictionary
    """
    required_keys = [
        'MQTT_HOST', 'MQTT_TOPIC_TEMP_PREFIX', 'MQTT_TOPIC_HUMID_PREFIX',
        'MQTT_USERNAME', 'MQTT_PASSWORD', 'DHT_PIN'
    ]
    
    config = {}
    for key in required_keys:
        value = os.getenv(key)
        if not value:
            logger.error(f"Missing required environment variable: {key}")
            raise ValueError(f"Missing required environment variable: {key}")
        config[key] = value
    
    return config

def main():
    """Main entry point."""
    try:
        config = get_config()
        dht_pin = int(config['DHT_PIN'])
        
        while True:
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, dht_pin)
            
            if humidity is not None and temperature is not None:
                print(f"Temp={temperature:0.1f}*C  Humidity={humidity:0.1f}%")
                
                # Publish temperature
                publish.single(
                    config['MQTT_TOPIC_TEMP_PREFIX'],
                    temperature,
                    hostname=config['MQTT_HOST'],
                    client_id='enclosure',
                    auth={'username': config['MQTT_USERNAME'], 'password': config['MQTT_PASSWORD']}
                )
                logger.info(f"Enclosure Temperature -> {round(temperature, 1)}")
                
                # Publish humidity
                publish.single(
                    config['MQTT_TOPIC_HUMID_PREFIX'],
                    humidity,
                    hostname=config['MQTT_HOST'],
                    client_id='enclosure',
                    auth={'username': config['MQTT_USERNAME'], 'password': config['MQTT_PASSWORD']}
                )
                logger.info(f"Enclosure Humidity -> {round(humidity, 1)}")
            else:
                logger.error("Failed to retrieve data from humidity sensor")
                
            time.sleep(DELAY)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()