#!/usr/bin/env python3
import time
import subprocess
import urllib.request
import easygopigo3

RELAY_URL_ON = 'http://127.0.0.1:8088/on'
RELAY_URL_OFF = 'http://127.0.0.1:8088/off'
AUDIO_FILE = '/home/pi/ghost_moan_15s.wav'
AUDIO_DEVICE = 'plughw:2,0'
TRIGGER_DISTANCE_CM = 120.0
COOLDOWN_SEC = 5.0

def set_light(state: bool):
    url = RELAY_URL_ON if state else RELAY_URL_OFF
    for attempt in range(3):
        try:
            urllib.request.urlopen(url, timeout=2)
            break
        except Exception as e:
            if attempt == 2:
                print(f'Light toggle warning: {e}')
            time.sleep(0.2)

# Ensure tapo_relay micro-service is running
try:
    urllib.request.urlopen(RELAY_URL_OFF, timeout=1)
except Exception:
    print('Starting Tapo relay micro-service...')
    subprocess.Popen([
        '/home/pi/tapo_env/bin/python', '/home/pi/tapo_relay.py'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

# Make sure light starts in OFF state
set_light(False)

print('Initializing GoPiGo3 hardware...')
gpg = easygopigo3.EasyGoPiGo3()
try:
    ds = gpg.init_distance_sensor()
    print('Time-of-Flight distance sensor active!')
except Exception as e:
    print('Falling back to ultrasonic sensor...')
    ds = gpg.init_ultrasonic_sensor()

# Glowing red eyes in standby
gpg.set_eye_color((255, 0, 0))
gpg.open_eyes()

print('==================================================')
print('  HALLOWEEN SCARE MACHINE ARMED AND READY!')
print('  - Duration: 15 SECONDS per scare')
print('  - Light: Tapo TP15 Smart Plug (192.168.1.105)')
print('  - Audio: Jabra SPEAK 510 USB (Ghostly OOOOOO wail)')
print('  - Trigger Threshold: < 120 cm')
print('==================================================')

try:
    while True:
        try:
            dist = ds.read_mm() / 10.0
        except Exception:
            dist = 999.0

        if 5.0 < dist < TRIGGER_DISTANCE_CM:
            print(f'>>> TRIGGERED! Distance: {dist:.1f} cm (Starting 15s Ghost Scare) <<<')

            # 1. Snap spotlight ON
            set_light(True)

            # 2. Play 15-second ghostly OOOOOO wail on Jabra speaker
            subprocess.run(['aplay', '-D', AUDIO_DEVICE, '-q', AUDIO_FILE])

            # 3. Turn spotlight OFF
            set_light(False)
            print('>>> Scare complete. Cooldown for 5 seconds... <<<')

            # 4. Wait cooldown
            time.sleep(COOLDOWN_SEC)

        time.sleep(0.1)

except KeyboardInterrupt:
    print('Disarming scare machine...')
    set_light(False)
    gpg.close_eyes()
