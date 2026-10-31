#!/usr/bin/env python3
import time
import subprocess
import urllib.request
import easygopigo3

RELAY_URL_ON = 'http://127.0.0.1:8088/on'
RELAY_URL_OFF = 'http://127.0.0.1:8088/off'
AUDIO_FILE = '/home/pi/witch_laugh_10s.wav'
AUDIO_DEVICE = 'plughw:2,0'
TRIGGER_DISTANCE_CM = 220.0  # Max sensor detection threshold in cm (~7.2 feet)
COOLDOWN_SEC = 5.0          # Seconds to wait after scare finishes

def set_light(state: bool):
    url = RELAY_URL_ON if state else RELAY_URL_OFF
    for attempt in range(3):
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except Exception as e:
            if attempt == 2:
                print(f'[WARN] Light toggle error: {e}', flush=True)
            time.sleep(0.2)
    return False

# Ensure relay service is alive
relay_ok = False
for _ in range(5):
    try:
        urllib.request.urlopen(RELAY_URL_OFF, timeout=1)
        relay_ok = True
        break
    except Exception:
        print('Starting Tapo relay microservice...', flush=True)
        subprocess.Popen([
            '/home/pi/tapo_env/bin/python', '/home/pi/tapo_relay.py'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)

if relay_ok:
    print('Tapo Smart Plug Relay is ACTIVE and READY.', flush=True)
else:
    print('[WARN] Tapo Smart Plug Relay failed to respond.', flush=True)

# Turn off light initially
set_light(False)

print('Initializing GoPiGo3 hardware...', flush=True)
gpg = easygopigo3.EasyGoPiGo3()
try:
    ds = gpg.init_distance_sensor()
    print('Time-of-Flight distance sensor ACTIVE.', flush=True)
except Exception as e:
    print('Falling back to ultrasonic sensor...', flush=True)
    ds = gpg.init_ultrasonic_sensor()

# Blood red eye glow in standby
gpg.set_eye_color((255, 0, 0))
gpg.open_eyes()

print('==================================================', flush=True)
print('  HALLOWEEN SCARE MACHINE ARMED AND MONITORING!', flush=True)
print('  - Trigger Threshold: < 150 cm', flush=True)
print('  - Duration: 10 Seconds (Witch Laugh + Spotlight)', flush=True)
print('==================================================', flush=True)

last_status_time = 0

try:
    while True:
        try:
            dist = ds.read_mm() / 10.0
        except Exception as e:
            dist = 999.0

        # Heartbeat log every 3 seconds so we can see live distance in logs
        now = time.time()
        if now - last_status_time > 3.0:
            print(f'[Standby] Current distance reading: {dist:.1f} cm', flush=True)
            last_status_time = now

        if 5.0 < dist < TRIGGER_DISTANCE_CM:
            print(f'>>> SCARE TRIGGERED! Target at: {dist:.1f} cm <<<', flush=True)

            # 1. Light ON
            set_light(True)

            # 2. Play 10s witch laugh
            subprocess.run(['aplay', '-D', AUDIO_DEVICE, '-q', AUDIO_FILE])

            # 3. Light OFF
            set_light(False)
            print(f'>>> Scare complete. Cooldown for {COOLDOWN_SEC}s... <<<', flush=True)

            # 4. Cooldown
            time.sleep(COOLDOWN_SEC)
            last_status_time = time.time()

        time.sleep(0.1)

except KeyboardInterrupt:
    print('Disarming scare machine...', flush=True)
    set_light(False)
    gpg.close_eyes()
