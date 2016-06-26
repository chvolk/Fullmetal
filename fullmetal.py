import sys
sys.path.append('../lib/')

import threading
import subprocess
from vibration_type import VibrationType
import pdb
from lifxlan import LifxLAN
from phue import Bridge
from ouimeaux.environment import Environment
from myo import Myo
import requests
from device_listener import DeviceListener
from pose_type import PoseType
import time
import datetime

print('Getting light info')

#FOR LIFX LIGHTS
print("Finding LIFX lights")
num_lights = 2
lifx = LifxLAN(num_lights)
devices = lifx.get_lights()
if 'Bedroom' in str(devices[1]):
    bedside_table_light = devices[0]
    bedroom_light = devices[1]

else:
    bedside_table_light = devices[1]
    bedroom_light = devices[0]


#FOR PHILLIPS HUE LIGHTS
#FIRST GET THE IP OF THE BRIDGE (use $ arp -a)
print('Finding Hue lights')
b = Bridge('192.168.1.115')
light_names = b.get_light_objects('name')

# IF YOU WANT TO USE ACTIVITIES FROM A HARMONY HUB ENTER THE INFO HERE
harmony_start_url = "https://home.myharmony.com/cloudapi/hub/8191553/activity/18750134/start"
harmony_end_url = "https://home.myharmony.com/cloudapi/hub/8191553/activity/18750134/end"

#PAYLOAD IS USUALLY EMPTY (LEAVE IT AS "")
harmony_payload = ""

#USE POSTMAN TO GET THIS INFO
harmony_start_headers = {
    'authorization': "Bearer uJ7gfqjodZfG9A-hVuposA;MeW6q7lPtKJ2VEvo1LVqgn_A01eJx4LwiUJ1gY7Qep0",
    'cache-control': "no-cache",
    'postman-token': "5d8cbbee-7803-2034-f490-4cbe00a2e9f1"
    }

harmony_end_headers = {
    'authorization': "Bearer uJ7gfqjodZfG9A-hVuposA;MeW6q7lPtKJ2VEvo1LVqgn_A01eJx4LwiUJ1gY7Qep0",
    'cache-control': "no-cache",
    'postman-token': "4bfa6299-c26c-0de8-28f1-de46b34ceb48"
    }

#EDIT THIS COMMAND TO CONTAIN THE MAC ADDRESS OF THE DEVICE YOU WANT TO USE TO GAUGE DISTANCE
command = 'hcitool rssi 70:3E:AC:16:97:98'



#Find and connect to WeMo Devices.
print('Finding WeMo devices')
def on_switch(switch): 
    print "Switch found!", switch.name

env = Environment(on_switch)
env.start()
aircon = env.get_switch('Air Conditioner')
fan = env.get_switch('Fan')

#Set global locks
bedroom_locked = None
livingroom_locked = None
harmony_lock = None
wemo_lock = None

idle_loop_check = None

#Start up Myo
print('Starting Fullmetal')

fullmetal = Myo()
fullmetal.connect()

#Set start time in file
with open("time_record.txt", "w") as text_file:
        start_time = time.time()
        text_file.write(str(start_time))
old_result = None

class PrintPoseListener(DeviceListener):
        def __init__(self):
                global bedroom_locked
                global livingroom_locked
                global harmony_lock
                global wemo_lock
                bedroom_locked = True
                livingroom_locked = True
                harmony_lock = True
                wemo_lock = True
                self.active_pose = None
                self.current_room = None
                
        def on_pose(self, pose):
                global bedroom_locked
                global livingroom_locked
                global harmony_lock
                global wemo_lock
                pose_type = PoseType(pose)
                self.active_pose = pose_type.name

                print(pose_type.name)

                with open("time_record.txt", "w") as text_file:
                    pose_time = time.time()
                    text_file.write(str(pose_time))

                #Get an average signal strength
                range_gauge = []
                for i in range(10):
                    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
                    output = int(str(process.communicate()[0]).replace('RSSI return value: ', ''))
                    range_gauge.append(output)
                distance = sum(range_gauge) / float(len(range_gauge))

                # If signal strength is below -3, know that i'm in another room
                if distance < -3:
                    self.current_room = 'LIVING'
                else:
                    self.current_room = 'BED'
                
                #If in bedroom and want to turn on the lights or projector
                if self.active_pose == 'WAVE_OUT' and bedroom_locked is True and self.current_room == 'BED':
                        bedroom_locked = False
                        fullmetal.vibrate(VibrationType.SHORT)
                        fullmetal.vibrate(VibrationType.SHORT)
                        #myo.vibrate(VibrationType.SHORT)
                        #myo.vibrate(VibrationType.SHORT)
                        print("Bedroom unlocked")
                        time.sleep(.5)

                #if in living room and want to turn on the lights
                elif self.active_pose == 'WAVE_OUT' and livingroom_locked is True and self.current_room == 'LIVING':
                        fullmetal.vibrate(VibrationType.SHORT)
                        fullmetal.vibrate(VibrationType.SHORT)
                        livingroom_locked = False
                        print("Living room unlocked")
                        time.sleep(.5)

                #Unlock WeMo devices
                if self.active_pose == 'DOUBLE_TAP' and harmony_lock is True and self.current_room == 'BED':
                        wemo_lock = False
                        fullmetal.vibrate(VibrationType.SHORT)
                        print("WeMo Unlocked")

                #Turn on WeMo Device
                if self.active_pose == 'FINGERS_SPREAD' and wemo_lock is False and self.current_room == 'BED':
                        aircon.on()
                        wemo_lock = True
                        fullmetal.vibrate(VibrationType.SHORT)
                        print('Air conditioner on')

                #Turn off WeMo device
                if self.active_pose == 'FIST' and wemo_lock is False and self.current_room == 'BED':
                        aircon.off()
                        wemo_lock = True
                        fullmetal.vibrate(VibrationType.SHORT)
                        print('Air conditioner off')

                #if in bedroom and want to turn on/off the projector 
                elif self.active_pose == 'DOUBLE_TAP' and bedroom_locked is False and self.current_room == 'BED':
                        if harmony_lock is True:
                            harmony_lock = False
                            harmony_status = "OFF"
                            fullmetal.vibrate(VibrationType.MEDIUM)
                        elif harmony_lock is False:
                            harmony_lock = True
                            harmony_status = "ON"
                            fullmetal.vibrate(VibrationType.SHORT)
                        print("Harmony lock is {}".format(harmony_status))

                #Turn on the lights in bedroom
                elif self.active_pose == 'FINGERS_SPREAD' and bedroom_locked is False and harmony_lock is True and self.current_room == 'BED':
                        fullmetal.vibrate(VibrationType.SHORT)
                        lifx.set_power_all_lights(True)
                        #self.original_powers = lifx.get_power_all_lights()
                        #self.original_colors = lifx.get_color_all_lights()
                        bedroom_locked = True
                        #myo.vibrate(VibrationType.SHORT)
                        print("Bedroom lights on")

                #Turn on the living room lights
                elif self.active_pose == 'FINGERS_SPREAD' and livingroom_locked is False and harmony_lock is True and self.current_room == 'LIVING':
                        fullmetal.vibrate(VibrationType.SHORT)
                        light_names['Living room light'].on = True
                        light_names['Kitchen Light'].on = True
                        light_names['Doorway light'].on = True
                        light_names['Living room table light'].on = True
                        light_names['Kitchen light 2'].on = True
                        livingroom_locked = True
                        #myo.vibrate(VibrationType.SHORT)
                        print("Living room lights on")

                #Turn on the projector
                elif self.active_pose == 'FINGERS_SPREAD' and bedroom_locked is False and harmony_lock is False and self.current_room == 'BED':
                        # response = harmony_switch('ON')
                        harmony_lock = True
                        bedroom_locked = True
                        fullmetal.vibrate(VibrationType.SHORT)
                        print("Projector on")

                #Turn off the bedroom lights
                elif self.active_pose == 'FIST' and bedroom_locked is False and harmony_lock is True  and self.current_room == 'BED':
                        fullmetal.vibrate(VibrationType.SHORT)
                        lifx.set_power_all_lights(False)
                        bedroom_locked = True
                        print("Bedroom lights off")

                #Turn off the living room lights        
                elif self.active_pose == 'FIST' and livingroom_locked is False and harmony_lock is True and self.current_room == 'LIVING':
                        fullmetal.vibrate(VibrationType.SHORT)
                        light_names['Living room light'].on = False
                        light_names['Kitchen Light'].on = False
                        light_names['Doorway light'].on = False
                        light_names['Living room table light'].on = False
                        light_names['Kitchen light 2'].on = False
                        livingroom_locked = True
                        print("Living room lights off")

                #Turn off the projector
                elif self.active_pose == 'FIST' and bedroom_locked is False and harmony_lock is False and self.current_room == 'BED':
                        # response = harmony_switch('OFF')
                        harmony_lock = True
                        bedroom_locked = True
                        fullmetal.vibrate(VibrationType.SHORT)
                        print("Projector off")

                #lock everything
                elif self.active_pose == 'WAVE_IN':
                        bedroom_locked = True
                        livingroom_locked = True
                        harmony_lock = True
                        wemo_lock = True
                        fullmetal.vibrate(VibrationType.SHORT)
                        time.sleep(1)
                        print("Locked")

                if self.active_pose == 'REST':
                    pass

#Checks for idle and locks the device after n seconds if no activity is detected after unlock
def check_for_idle():
    global fullmetal
    global bedroom_locked
    global livingroom_locked
    global harmony_lock
    global wemo_lock
    global idle_loop_check
    idle_loop_check = True
    while idle_loop_check:
        try:
            time.sleep(1)
            with open('time_record.txt', 'r') as time_record:
                then=float(time_record.read().replace('\n', ''))
            now = time.time()
            diff = round(now - then)
            print diff

            if diff >= 3 and (bedroom_locked is False or livingroom_locked is False or harmony_lock is False):
                print('Idle Lock')
                bedroom_locked = True
                livingroom_locked = True
                harmony_lock = True
                wemo_lock = True
                fullmetal.vibrate(VibrationType.SHORT)

            # elif diff >= 100:
            #     print('Idle for too long. Reconnecting')
            #     try:
            #         fullmetal.safely_disconnect()
            #         time.sleep(3)
            #         fullmetal = Myo()
            #         add_listener(fullmetal)
            #         fullmetal.connect()
            #         start()
            #         idle_loop_check = False
            #     except Exception as e:
            #         print(e)
            #         pass

        except Exception as e:
            print(e)
            pass

def harmony_switch(status):
    if status == 'ON':
        response = requests.post(harmony_start_url, data=harmony_payload, headers=harmony_start_headers)
    elif status == 'OFF':
        response = requests.post(harmony_end_url, data=harmony_payload, headers=harmony_end_headers)
    return response

def add_listener(myo):
    listener = PrintPoseListener()
    fullmetal.add_listener(listener)

def start():
    global idle_loop_check 
    try:
        time.sleep(2)
        idle_checker = threading.Thread(target=check_for_idle).start()
        while True:
            fullmetal.run()
        print("Run loop ended")

    except Exception as ex:
        print('Generic Exception')
        idle_loop_check = False
        time.sleep(2)
        print(ex)
    finally:
        fullmetal.safely_disconnect()
        print('Finished.')

if __name__ == '__main__':
    add_listener(fullmetal)
    try:
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output = str(process.communicate()[0])
        if 'RSSI' not in output:
            raise Exception('No Bluetooth Device Connected to use for distance gauge')
        start()
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        idle_loop_check = False
        time.sleep(2)
        sys.exit(0)
        pass
    except Exception as ex:
        print('Generic Exception')
        idle_loop_check = False
        time.sleep(2)
        print(ex)
    finally:
        print('Finished.')
