# 3D Enclosure Scripts

This project contains scripts for controlling and monitoring a 3D printer enclosure using a Raspberry Pi.

## Features

- Temperature and humidity monitoring using DHT22 sensor
- Fan control via MQTT
- Integration with Home Assistant
- Systemd journal logging

## Prerequisites

- Python 3.x
- Raspberry Pi with GPIO access
- DHT22 sensor
- MQTT broker (e.g., Home Assistant)

## Installation

1. Install system dependencies:
```bash
sudo apt install python3-pip libsystemd-dev
```

2. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your configuration:
```env
# MQTT Configuration
MQTT_HOST=your_mqtt_broker_ip
MQTT_TOPIC_FAN_PREFIX=fan/extractor
MQTT_TOPIC_FAN_STATUS_PREFIX=fan/extractor/status
MQTT_TOPIC_TEMP_PREFIX=enclosure/temperature
MQTT_TOPIC_HUMID_PREFIX=enclosure/humidity

# MQTT Authentication
MQTT_USERNAME=your_username
MQTT_PASSWORD=your_password

# GPIO Configuration
GPIO_PIN=24
DHT_PIN=4
```

## Usage

1. Start the fan control service:
```bash
python3 mqtt_subscriber.py
```

2. Start the temperature/humidity monitoring:
```bash
python3 humidity.py
```

## Systemd Service Setup

1. Create systemd service files for both scripts
2. Enable and start the services:
```bash
sudo systemctl enable enclosure-fan
sudo systemctl enable enclosure-monitor
sudo systemctl start enclosure-fan
sudo systemctl start enclosure-monitor
```

## Logging

Logs are written to the systemd journal. View logs with:
```bash
journalctl -u enclosure-fan
journalctl -u enclosure-monitor
```
