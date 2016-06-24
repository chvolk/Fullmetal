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


# IF YOU WANT TO USE ACTIVITIES FROM A HARMONY HUB YOU NEED TO ENTER THE INFO HERE
harmony_start_url = ""
harmony_end_url = ""

#PAYLOAD IS USUALLY EMPTY (LEAVE IT AS "")
harmony_payload = ""

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
                
        def on_pose(self, pose):
                pose_type = PoseType(pose)
                self.active_pose = pose_type.name

                print(pose_type.name)
                # if self.active_pose == 'REST':
                #     self.bedroom_locked = True
                #     self.livingroom_locked = True

                #If in bedroom and want to turn on the lights or projector
                if self.active_pose == 'WAVE_OUT' and self.bedroom_locked is True:
                        self.bedroom_locked = False
                        vibrate('SHORT')
                        vibrate('SHORT')
                        #myo.vibrate(VibrationType.SHORT)
                        #myo.vibrate(VibrationType.SHORT)
                        print("Bedroom unlocked")
                        time.sleep(.5)

                #if in living room and want to turn on the lights
                elif self.active_pose == 'DOUBLE_TAP' and self.livingroom_locked is True and self.bedroom_locked is True:
                        vibrate('SHORT')
                        vibrate('SHORT')
                        self.livingroom_locked = False
                        print("Living room unlocked")
                        time.sleep(.5)

                #if in bedroom and want to turn on/off the projector 
                elif self.active_pose == 'DOUBLE_TAP' and self.livingroom_locked is True and self.bedroom_locked is False:
                        if self.harmony_lock is True:
                            self.harmony_lock = False
                            harmony_status = "OFF"
                            vibrate('MED')
                        elif self.harmony_lock is False:
                            self.harmony_lock = True
                            harmony_status = "ON"
                            vibrate('SHORT')
                        print("Harmony lock is {}".format(harmony_status))

                #Turn on the lights in bedroom
                elif self.active_pose == 'FINGERS_SPREAD' and self.bedroom_locked is False and self.livingroom_locked is True and self.light_status == 'OFF' and self.harmony_lock is True:
                        vibrate('SHORT')
                        lifx.set_power_all_lights(True)
                        #self.original_powers = lifx.get_power_all_lights()
                        #self.original_colors = lifx.get_color_all_lights()
                        self.bedroom_locked = True
                        #myo.vibrate(VibrationType.SHORT)
                        self.light_status = 'ON'
                        print("Bedroom lights on")

                #Turn on the living room lights
                elif self.active_pose == 'FINGERS_SPREAD' and self.bedroom_locked is True and self.livingroom_locked is False and self.light_status == 'OFF' and self.harmony_lock is True:
                        vibrate('SHORT')
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
                elif self.active_pose == 'FINGERS_SPREAD' and self.bedroom_locked is False and self.livingroom_locked is True and self.harmony_lock is False:
                        harmony_switch('ON')
                        print(response)
                        self.harmony_lock = True
                        self.bedroom_locked = True
                        vibrate('SHORT')
                        print("Projector on")

                #Turn off the bedroom lights
                elif self.active_pose == 'FIST' and self.bedroom_locked is False and self.livingroom_locked is True and self.light_status == 'ON' and self.harmony_lock is True:
                        vibrate('SHORT')
                        lifx.set_power_all_lights(False)
                        self.bedroom_locked = True
                        self.light_status = 'OFF'
                        print("Bedroom lights off")

                #Turn off the living room lights        
                elif self.active_pose == 'FIST' and self.bedroom_locked is True and self.livingroom_locked is False and self.light_status == 'ON' and self.harmony_lock is True:
                        vibrate('SHORT')
                        light_names['Living room light'].on = False
                        light_names['Kitchen Light'].on = False
                        light_names['Doorway light'].on = False
                        light_names['Living room table light'].on = False
                        light_names['Kitchen light 2'].on = False
                        self.livingroom_locked = True
                        self.light_status = 'OFF'
                        print("Living room lights off")

                #Turn off the projector
                elif self.active_pose == 'FIST' and self.bedroom_locked is False and self.livingroom_locked is True and self.harmony_lock is False:
                        harmony_switch('OFF')
                        print(response)
                        self.harmony_lock = True
                        self.bedroom_locked = True
                        vibrate('SHORT')
                        print("Projector off")

                #lock everything
                elif self.active_pose == 'WAVE_IN':
                        self.bedroom_locked = True
                        self.livingroom_locked = True
                        self.harmony_lock = True
                        vibrate('SHORT')
                        print("Locked")

def get_lights():
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
    b = Bridge('IP ADDRESS OF HUE BRIDGE')
    light_names = b.get_light_objects('name')


def harmony_switch(status):
    if status == 'ON':
        requests.post(harmony_start_url, data=harmony_payload, headers=harmony_start_headers)
    elif status == 'OFF':
        requests.post(harmony_end_url, data=harmony_payload, headers=harmony_end_headers)

def vibrate(vibration_type):
    if vibration_type == 'SHORT':
        fullmetal.vibrate(VibrationType.SHORT)
    elif vibration_type == 'MED':
        fullmetal.vibrate(VibrationType.MEDIUM)
    elif vibration_type == 'LONG':
        fullmetal.vibrate(VibrationType.LONG)

def main(): 
    get_lights()
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