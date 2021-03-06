# Fullmetal
Home Automation using A Raspberry Pi3, Logitech Harmony, Phillips Hue lights, LIFX Lights, Wemo devices, and Bluetooth proximity in Python


Thanks to Ramir0 and his project Myo4Linux (https://github.com/Ramir0/Myo4Linux), which is the foundation of this project.

Tested and working on Raspberry Pi 3

This program is called Fullmetal because it allows you to control your connected devices using a "Wave Out" gesture, which can be executed by simply waving out, or by doing [this clap gesture](http://i.imgur.com/dEYs0ik.gif) from Fullmetal Alchemist.


## Pre-requirements for your Myo device
- Firmware version 1.3.1448 or higher
- It is necessary to calibrate your Myo device
- Use the Myo bluetooth dongle

## Requirements
- a Raspberry Pi 3
- python >=2.6
- pySerial
- enum34
- Myo4Linux (https://github.com/Ramir0/Myo4Linux)
- phue
- lifxlan
- bluez
- pi-bluetooth
- hcitool
- nmap
- requests
- ouimeaux



## Install

- Open the terminal (or using ssh to your Pi. See how to do this below if you need to)
- $ sudo apt-get update
- $ sudo apt-get upgrade -y
- $ sudo apt-get dist-upgrade -y
- $ sudo rpi-update
- $ sudo apt-get install pi-bluetooth
- $ sudo apt-get install bluez bluez-firmware
- $ sudo apt-get install blueman
- $ sudo apt-get install nmap
- $ git clone https://github.com/Ramir0/Myo4Linux.git
- $ sudo apt-get install python-pip (if not done already)
- $ sudo pip install -U pip
- $ sudo pip install pySerial
- $ sudo pip install enum34
- $ sudo pip install phue
- $ sudo pip install lifxlan
- $ sudo pip install ouimeaux
- $ sudo pip install requests

## SSH into Raspberry Pi
- $ nmap -sL 192.168.1.1/24
- Wait a while for nmap to run. Once it returns a list of IPs find the line that reads "Nmap scan report for raspberrypi (IP-ADDRESS)". Copy the ip adress. 
- Open the terminal
- $ ssh i IP-ADDRESS-OF-PI
- Enter the password of your raspberry pi


## Set up WeMo Devices

- $ python
- $ import ouimeaux
- $ from ouimeaux.environment import Environment
- $ env = Environment()
- $ env.start()
- $ env.discover(20)
- $ print env.list_switches()
- This will list the devices. Use the device names listed and add those to the code in the wemo setup section. Edit the code in the Wemo section near the top to have the appropriate device names. You only have to do this once.

## Set up Hue Bridge

- $ nmap -sL 192.168.1.1/24
- Wait a while for nmap to run. Once it returns a list of IPs find the line that reads "Nmap scan report for Philips-hue (IP-ADRESS)". Copy the ip adress. 
- $ python
- $ from phue import Bridge
- Press the connect button on the Hue bridge
- $ b = Bridge('IP-ADDRESS-OF-YOUR-BRIDGE')
- $ b.connect()
- $ print b.lights
- This will return the list of lights available. Edit the code where necessary with the proper light names. You only have to do this once. 

## Set up LIFX Lights
- Edit the code in fullmetal.py in the LIFX section near the top to work with the number of lights you have (num_lights) and find the light names and then assign lights to values using the appropriate names. 

## Set Up Logitech Harmony
- Edit the code in the Harmony section near the top to contain the appropriate info for the API calls to start/stop your activity. You can get this info using the Postman app for Chrome (recommended by the Logitech Harmony team)

## Pair Pi to phone using bluetooth (for distance sensing when you want to control lights in one room, but not another one with the same gestures)

- $ sudo bluetoothctl -ahciconfig hci0 sspmode 1^C
- $ sudo hciconfig hci0 sspmode 1
- $ sudo hciconfig hci0 sspmode
- $ sudo hciconfig hci0 piscan
- $ sudo sdptool add SP
- $ sudo hcitool scan
- (Find the bluetooth MAC address of the device you want to connect to EX: 70:3O:AC:00:00:70)
- $ sudo rfcomm connect /dev/rfcomm0 DEVICE-MAC-ADDRESS-HERE 1 &
- $ hcitool rsii DEVICE-MAC-ADDRESS-HERE (to test if it all works. should return something like "RSSI return value: -1")
- You should only have to do this process once. After you do this, you can connect to the Pi3 from your phone (or whatever device) the way you would normally connect to any other bluetooth device. Kepp in mind that you have to connect the device every time you restart the Pi or have been disconnected from it before you run the code.
- Keep in mind that the bluetooth range of the Myo is limited to about 20-30 ft (depending on interference), so you can use this code to differentiate between being in one of two rooms (ex. Living Room vs Bedrrom). This is also due to limitations regarding the use of bluetooth RSSI signal strength as a gauge of distance. 

## Steps:

- The Myo dongle bluetooth must be connected.
- Add Fullmetal (or your edited version of it) to the "sample" folder in Myo4Linux (or port the files from Myo4Linux to wherever you want and run the code from there)
- Edit the code to use the proper RSSI values (bluetooth signal strength) for the area you'll be using it in. 
- Edit the code to properly name and find all of your lights and devices and whatnot.
- You need to pair with your bluetooth device before you run the code to sense distance. 
- python fullmetal.py



