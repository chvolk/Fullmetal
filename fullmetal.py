import sys
sys.path.append('../lib/')

import threading
import subprocess
from myo import Myo
from vibration_type import VibrationType
import pdb
from lifxlan import LifxLAN
from phue import Bridge
from myo import Myo
from vibration_type import VibrationType
import requests
from device_listener import DeviceListener
from pose_type import PoseType
import time

fullmetal = None
light_status = None

print('Getting light info')
#FOR LIFX LIGHTS
num_lights = 2
lifx = LifxLAN(num_lights)
devices = lifx.get_lights()
if 'Bedroom' in str(devices[1]):
    bedside_table_light = devices[0]
    bedroom_light = devices[1]

else:
    bedside_table_light = devices[1]
    bedroom_light = devices[0]

original_powers = lifx.get_power_all_lights()
light_power1 = str(original_powers[0][0])
light_power2 = str(original_powers[1][0])

if 'Power: Off' in light_power1 and 'Power: Off' in light_power2:
    light_status = 'OFF'
else:
    light_status = 'ON'

#FOR PHILLIPS HUE LIGHTS
#FIRST GET THE IP OF THE BRIDGE (use $ arp -a)
b = Bridge('BRIDGE IP')
light_names = b.get_light_objects('name')

# IF YOU WANT TO USE ACTIVITIES FROM A HARMONY HUB ENTER THE INFO HERE
harmony_start_url = ""
harmony_end_url = ""

#PAYLOAD IS USUALLY EMPTY (LEAVE IT AS "")
harmony_payload = ""

#USE POSTMAN TO GET THIS INFO
harmony_start_headers = {
    'authorization': "",
    'cache-control': "",
    'postman-token': ""
    }

harmony_end_headers = {
    'authorization': "",
    'cache-control': "",
    'postman-token': ""
    }

#EDIT THIS COMMAND TO CONTAIN THE MAC ADDRESS OF THE DEVICE YOU WANT TO USE TO GAUGE DISTANCE
command = 'hcitool rssi MAC-ADDRESS'
print('Starting Fullmetal')

fullmetal = Myo()
fullmetal.connect()

class PrintPoseListener(DeviceListener):
        def __init__(self):
                self.bedroom_locked = True
                self.livingroom_locked = True
                self.active_pose = None
                self.harmony_lock = True
                self.light_status = light_status
                self.current_room = None
                
        def on_pose(self, pose):
                pose_type = PoseType(pose)
                self.active_pose = pose_type.name

                print(pose_type.name)
                range_gauge = []
                for i in range(10):
                    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
                    output = int(str(process.communicate()[0]).replace('RSSI return value: ', ''))
                    range_gauge.append(output)
                distance = sum(range_gauge) / float(len(range_gauge))
                if distance < -1:
                    self.current_room = 'LIVING':
                else:
                    self.current_room = 'BED'
                #If in bedroom and want to turn on the lights or projector
                if self.active_pose == 'WAVE_OUT' and self.bedroom_locked is True and self.current_room == 'BED'::
                        self.bedroom_locked = False
                        fullmetal.vibrate(VibrationType.SHORT)
                        fullmetal.vibrate(VibrationType.SHORT)
                        #myo.vibrate(VibrationType.SHORT)
                        #myo.vibrate(VibrationType.SHORT)
                        print("Bedroom unlocked")
                        time.sleep(.5)

                #if in living room and want to turn on the lights
                elif self.active_pose == 'WAVE_OUT' and self.livingroom_locked is True and self.current_room == 'LIVING':
                        fullmetal.vibrate(VibrationType.SHORT)
                        fullmetal.vibrate(VibrationType.SHORT)
                        self.livingroom_locked = False
                        print("Living room unlocked")
                        time.sleep(.5)

                #if in bedroom and want to turn on/off the projector 
                elif self.active_pose == 'DOUBLE_TAP' and self.bedroom_locked is False and self.current_room = 'BED':
                        if self.harmony_lock is True:
                            self.harmony_lock = False
                            harmony_status = "OFF"
                            fullmetal.vibrate(VibrationType.MEDIUM)
                        elif self.harmony_lock is False:
                            self.harmony_lock = True
                            harmony_status = "ON"
                            fullmetal.vibrate(VibrationType.SHORT)
                        print("Harmony lock is {}".format(harmony_status))

                #Turn on the lights in bedroom
                elif self.active_pose == 'FINGERS_SPREAD' and self.bedroom_locked is False and self.light_status == 'OFF' and self.harmony_lock is True and self.current_room == 'BED':
                        fullmetal.vibrate(VibrationType.SHORT)
                        lifx.set_power_all_lights(True)
                        #self.original_powers = lifx.get_power_all_lights()
                        #self.original_colors = lifx.get_color_all_lights()
                        self.bedroom_locked = True
                        #myo.vibrate(VibrationType.SHORT)
                        self.light_status = 'ON'
                        print("Bedroom lights on")

                #Turn on the living room lights
                elif self.active_pose == 'FINGERS_SPREAD' and self.livingroom_locked is False and self.light_status == 'OFF' and self.harmony_lock is True and self.current_room == 'LIVING':
                        fullmetal.vibrate(VibrationType.SHORT)
                        light_names['Living room light'].on = True
                        light_names['Kitchen Light'].on = True
                        light_names['Doorway light'].on = True
                        light_names['Living room table light'].on = True
                        light_names['Kitchen light 2'].on = True
                        self.livingroom_locked = True
                        #myo.vibrate(VibrationType.SHORT)
                        self.light_status = 'ON'
                        print("Living room lights on")

                #Turn on the projector
                elif self.active_pose == 'FINGERS_SPREAD' and self.bedroom_locked is False and self.harmony_lock is False and self.current_room == 'BED':
                        harmony_switch('ON')
                        print(response)
                        self.harmony_lock = True
                        self.bedroom_locked = True
                        fullmetal.vibrate(VibrationType.SHORT)
                        print("Projector on")

                #Turn off the bedroom lights
                elif self.active_pose == 'FIST' and self.bedroom_locked is False and self.light_status == 'ON' and self.harmony_lock is True  and self.current_room == 'BED':
                        fullmetal.vibrate(VibrationType.SHORT)
                        lifx.set_power_all_lights(False)
                        self.bedroom_locked = True
                        self.light_status = 'OFF'
                        print("Bedroom lights off")

                #Turn off the living room lights        
                elif self.active_pose == 'FIST' and self.livingroom_locked is False and self.light_status == 'ON' and self.harmony_lock is True and self.current_room == 'LIVING':
                        fullmetal.vibrate(VibrationType.SHORT)
                        light_names['Living room light'].on = False
                        light_names['Kitchen Light'].on = False
                        light_names['Doorway light'].on = False
                        light_names['Living room table light'].on = False
                        light_names['Kitchen light 2'].on = False
                        self.livingroom_locked = True
                        self.light_status = 'OFF'
                        print("Living room lights off")

                #Turn off the projector
                elif self.active_pose == 'FIST' and self.bedroom_locked is False and self.harmony_lock is False and self.current_room == 'BED':
                        harmony_switch('OFF')
                        print(response)
                        self.harmony_lock = True
                        self.bedroom_locked = True
                        fullmetal.vibrate(VibrationType.SHORT)
                        print("Projector off")

                #lock everything
                elif self.active_pose == 'WAVE_IN':
                        self.bedroom_locked = True
                        self.livingroom_locked = True
                        self.harmony_lock = True
                        fullmetal.vibrate(VibrationType.SHORT)
                        print("Locked")


def harmony_switch(status):
    if status == 'ON':
        requests.post(harmony_start_url, data=harmony_payload, headers=harmony_start_headers)
    elif status == 'OFF':
        requests.post(harmony_end_url, data=harmony_payload, headers=harmony_end_headers)

def main(): 
    try:
        listener = PrintPoseListener()
        fullmetal.add_listener(listener)
        fullmetal.vibrate(VibrationType.SHORT)
        while True:
            fullmetal.run()
        print("Run loop ended")

    except KeyboardInterrupt:
        pass
    except ValueError as ex:
        print(ex)
    finally:
        fullmetal.safely_disconnect()
        print('Finished.')

if __name__ == '__main__':
    main()
