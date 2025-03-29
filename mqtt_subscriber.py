#!/usr/bin/python
"""
MQTT Subscriber for Enclosure Control System
This script subscribes to MQTT topics to control an enclosure fan and monitor its status.
It interfaces with Home Assistant through MQTT and controls GPIO pins on a Raspberry Pi.
"""

import logging
import os
import socket
import time
from typing import Optional, Dict
from dotenv import load_dotenv
from systemd.journal import JournalHandler
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

# Load environment variables
load_dotenv()

class EnclosureController:
    """Controls the enclosure fan and handles MQTT communication."""
    
    def __init__(self, config: Dict[str, str]):
        """
        Initialize the enclosure controller.
        
        Args:
            config: Dictionary containing configuration parameters
        """
        self.config = config
        self.client: Optional[mqtt.Client] = None
        self._setup_logging()
        self._setup_gpio()
        
    def _setup_logging(self) -> None:
        """Configure logging with systemd journal handler."""
        self.logger = logging.getLogger('enclosure_controller')
        self.logger.addHandler(JournalHandler())
        self.logger.setLevel(logging.INFO)
        
    def _setup_gpio(self) -> None:
        """Configure GPIO pins."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(int(self.config['GPIO_PIN']), GPIO.OUT)
        
    def _publish_status(self, status: int) -> None:
        """
        Publish fan status to MQTT.
        
        Args:
            status: Current status of the fan (0 or 1)
        """
        try:
            publish.single(
                self.config['MQTT_TOPIC_FAN_STATUS_PREFIX'],
                str(status),
                hostname=self.config['MQTT_HOST'],
                client_id='enclosure',
                auth={'username': self.config['MQTT_USERNAME'], 'password': self.config['MQTT_PASSWORD']}
            )
        except Exception as e:
            self.logger.error(f"Failed to publish status: {e}")
            
    def on_connect(self, client: mqtt.Client, userdata: dict, flags: dict, rc: int) -> None:
        """
        Callback for when MQTT client connects.
        
        Args:
            client: MQTT client instance
            userdata: User data passed to client
            flags: Connection flags
            rc: Result code
        """
        self.logger.info(f"Connected to MQTT broker with result code {rc}")
        state = GPIO.input(int(self.config['GPIO_PIN']))
        self._publish_status(state)
        client.subscribe(self.config['MQTT_TOPIC_FAN_PREFIX'])
        
    def on_message(self, client: mqtt.Client, userdata: dict, msg: mqtt.MQTTMessage) -> None:
        """
        Callback for when MQTT message is received.
        
        Args:
            client: MQTT client instance
            userdata: User data passed to client
            msg: Received message
        """
        self.logger.info(f"Received message: {msg.topic} {msg.payload}")
        
        if 'extractor' in msg.topic:
            payload = msg.payload.decode().lower()
            if 'off' in payload:
                GPIO.output(int(self.config['GPIO_PIN']), GPIO.LOW)
                self._publish_status(0)
            elif 'on' in payload:
                GPIO.output(int(self.config['GPIO_PIN']), GPIO.HIGH)
                self._publish_status(1)
                
    def connect(self) -> None:
        """Establish MQTT connection with retry logic."""
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                self.client = mqtt.Client()
                self.client.on_connect = self.on_connect
                self.client.on_message = self.on_message
                self.client.username_pw_set(
                    username=self.config['MQTT_USERNAME'],
                    password=self.config['MQTT_PASSWORD']
                )
                self.client.connect(self.config['MQTT_HOST'], 1883)
                self.client.loop_forever()
                break
            except Exception as e:
                self.logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    self.logger.error("Max retries reached. Exiting.")
                    raise
                    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.client:
            self.client.disconnect()
        GPIO.cleanup()
        self.logger.info("Cleanup completed")

def get_config() -> Dict[str, str]:
    """
    Get configuration from environment variables.
    
    Returns:
        Dict[str, str]: Configuration dictionary
    """
    required_keys = [
        'MQTT_HOST', 'MQTT_TOPIC_FAN_PREFIX', 'MQTT_TOPIC_FAN_STATUS_PREFIX',
        'MQTT_USERNAME', 'MQTT_PASSWORD', 'GPIO_PIN'
    ]
    
    config = {}
    for key in required_keys:
        value = os.getenv(key)
        if not value:
            logging.error(f"Missing required environment variable: {key}")
            raise ValueError(f"Missing required environment variable: {key}")
        config[key] = value
    
    return config

def main():
    """Main entry point."""
    try:
        config = get_config()
        controller = EnclosureController(config)
        controller.connect()
    except KeyboardInterrupt:
        logging.info("Received shutdown signal")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        if 'controller' in locals():
            controller.cleanup()

if __name__ == "__main__":
    main()
