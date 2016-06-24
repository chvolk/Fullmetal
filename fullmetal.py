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

b = Bridge('192.168.1.115')
light_names = b.get_light_objects('name')

start_url = "https://home.myharmony.com/cloudapi/hub/8191553/activity/18750134/start"
end_url = "https://home.myharmony.com/cloudapi/hub/8191553/activity/18750134/end"
payload = ""

start_headers = {
    'authorization': "Bearer uJ7gfqjodZfG9A-hVuposA;MeW6q7lPtKJ2VEvo1LVqgn_A01eJx4LwiUJ1gY7Qep0",
    'cache-control': "no-cache",
    'postman-token': "5d8cbbee-7803-2034-f490-4cbe00a2e9f1"
    }

end_headers = {
    'authorization': "Bearer uJ7gfqjodZfG9A-hVuposA;MeW6q7lPtKJ2VEvo1LVqgn_A01eJx4LwiUJ1gY7Qep0",
    'cache-control': "no-cache",
    'postman-token': "4bfa6299-c26c-0de8-28f1-de46b34ceb48"
    }

pdb.set_trace()
print('Start Myo for Linux')

fullmetal = Myo()
fullmetal.connect()
start_time = time.time()


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
                # pose_time = time.time()
                # rest_time = start_time - pose_time
                # if rest_time > 30:
                #     fullmetal.safely_disconnect()
                #     start_time = time.time()
                #     main()
                    
                # else:
                #     pass

                print(pose_type.name)
                # if self.active_pose == 'REST':
                #     self.bedroom_locked = True
                #     self.livingroom_locked = True

                #If in bedroom and want to turn on the lights or projector
                if self.active_pose == 'WAVE_OUT' and self.bedroom_locked is True:
                        self.bedroom_locked = False
                        fullmetal.vibrate(VibrationType.SHORT)
                        fullmetal.vibrate(VibrationType.SHORT)
                        #myo.vibrate(VibrationType.SHORT)
                        #myo.vibrate(VibrationType.SHORT)
                        print("Bedroom unlocked")
                        time.sleep(.5)

                #if in living room and want to turn on the lights
                elif self.active_pose == 'DOUBLE_TAP' and self.livingroom_locked is True and self.bedroom_locked is True:
                        fullmetal.vibrate(VibrationType.SHORT)
                        fullmetal.vibrate(VibrationType.SHORT)
                        self.livingroom_locked = False
                        print("Living room unlocked")
                        time.sleep(.5)

                #if in bedroom and want to turn on/off the projector 
                elif self.active_pose == 'DOUBLE_TAP' and self.livingroom_locked is True and self.bedroom_locked is False:
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
                elif self.active_pose == 'FINGERS_SPREAD' and self.bedroom_locked is False and self.livingroom_locked is True and self.light_status == 'OFF' and self.harmony_lock is True:
                        fullmetal.vibrate(VibrationType.SHORT)
                        lifx.set_power_all_lights(True)
                        #self.original_powers = lifx.get_power_all_lights()
                        #self.original_colors = lifx.get_color_all_lights()
                        self.bedroom_locked = True
                        #myo.vibrate(VibrationType.SHORT)
                        self.light_status = 'ON'
                        print("Bedroom lights on")

                #Turn on the living room lights
                elif self.active_pose == 'FINGERS_SPREAD' and self.bedroom_locked is True and self.livingroom_locked is False and self.light_status == 'OFF' and self.harmony_lock is True:
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
                elif self.active_pose == 'FINGERS_SPREAD' and self.bedroom_locked is False and self.livingroom_locked is True and self.harmony_lock is False:
                        response = requests.post(start_url, data=payload, headers=start_headers)
                        print(response)
                        self.harmony_lock = True
                        self.bedroom_locked = True
                        fullmetal.vibrate(VibrationType.SHORT)
                        print("Projector on")

                #Turn off the bedroom lights
                elif self.active_pose == 'FIST' and self.bedroom_locked is False and self.livingroom_locked is True and self.light_status == 'ON' and self.harmony_lock is True:
                        fullmetal.vibrate(VibrationType.SHORT)
                        lifx.set_power_all_lights(False)
                        self.bedroom_locked = True
                        self.light_status = 'OFF'
                        print("Bedroom lights off")

                #Turn off the living room lights        
                elif self.active_pose == 'FIST' and self.bedroom_locked is True and self.livingroom_locked is False and self.light_status == 'ON' and self.harmony_lock is True:
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
                elif self.active_pose == 'FIST' and self.bedroom_locked is False and self.livingroom_locked is True and self.harmony_lock is False:
                        response = requests.post(end_url, data=payload, headers=end_headers)
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

def check_output_status():
    output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]

def harmony_switch(status):
    if status == 'ON':
        requests.post(start_url, data=payload, headers=start_headers)
    elif status == 'OFF':
        requests.post(end_url, data=payload, headers=end_headers)

def vibrate(vibration_type):
    if vibration_type == 'SHORT':
        fullmetal.vibrate(VibrationType.SHORT)
    elif vibration_type == 'MED':
        fullmetal.vibrate(VibrationType.MEDIUM)
    elif vibration_type == 'LONG':
        fullmetal.vibrate(VibrationType.LONG)


if __name__ == '__main__':
    main()