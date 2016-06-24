# Fullmetal
Home Automation using Logitech Harmony, Phillips Hue lights, LIFX Lights, and Bluetooth proximity


Thanks to Ramir0 (https://github.com/Ramir0/Myo4Linux), which is the foundation of this project.

# Pre-requirements for your Myo device
- Firmware version 1.3.1448 or higher
- It is necessary to calibrate your Myo device using the official software.
- Use the Myo dongle bluetooth

# Requirements
- python >=2.6
- pySerial
- enum34
- Myo4Linux (https://github.com/Ramir0/Myo4Linux)
- phue
- lifxlan
- bluez
- pi-bluetooth
- hcitool


# Install

- Open the terminal
- $ sudo apt-get update
- $ sudo apt-get upgrade -y
- $ sudo apt-get dist-upgrade -y
- $ sudo rpi-update
- $ sudo apt-get install pi-bluetooth
- $ sudo apt-get install bluez bluez-firmware
- $ sudo apt-get install blueman
- $ sudo apt-get install pip (if not done already)
- $ sudo pip install phue
- $ sudo pip install lifxlan
- $ sudo pip install requests

# Steps:
- The Myo dongle bluetooth must be connected.
- Add Fullmetal (or your edited version of it) to the "sample" folder in Myo4Linux (or port the files from Myo4Linux to wherever you want and run the code from there)
- python fullmetal.py