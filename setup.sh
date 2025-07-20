#!/bin/bash

# Please follow the steps found here before running this script!: https://www.notion.so/How-to-setup-bridge-to-emqx-1b5cfd52ac1880928fa6f82500905546

# Install Python packages - to be ran on raspberry pi
sudo apt update
sudo apt upgrade
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto

sudo apt install -y python3-bme280
sudo apt install -y python3-load_dotenv
sudo apt install -y python3-gpiozero
sudo apt install -y python3-paho-mqtt
sudo apt install -y i2c-tools
sudo apt install -y python3-smbus
sudo apt install -y build-essential

# Run the weather service
cd ~/nimbus-pi
python3 weather-service.py