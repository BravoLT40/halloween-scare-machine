# 🎃 GoPiGo3 Halloween Scare Machine

An automated, standalone Halloween scare machine powered by a **Dexter Industries GoPiGo3** (Raspberry Pi 3B), a **Time-of-Flight distance sensor**, a **TP-Link Tapo Smart Plug (Matter/TP15)** controlling a high-power spotlight, and an amplified USB speaker (**Jabra SPEAK 510**).

---

## Architecture & How It Works

```
                                      +------------------------+
                                      |   Halloween Skeleton   |
                                      +------------------------+
                                                  ^
                                                  | (15s Spotlight Beam)
                                                  |
[ Walkway ] ==================================> [ Tapo TP15 Smart Plug ]
                                                (192.168.1.105:80)
     |                                                    ^
     | (Trick-or-treaters enter < 120 cm)                 |
     v                                                    | (Local HTTP relay)
+---------------------------------------------------------+----+
|  GoPiGo3 Rover (Hidden in Bushes)                            |
|                                                              |
|  1. ToF Distance Sensor (I2C) trips when distance < 120 cm   |
|  2. GoPiGo eye LEDs glow blood red                           |
|  3. Sends local command: http://127.0.0.1:8088/on            |
|  4. Jabra SPEAK 510 USB blasts 15s ghostly vocal wail        |
|  5. Sends local command: http://127.0.0.1:8088/off           |
|  6. Cooldown 5s before re-arming                             |
+--------------------------------------------------------------+
```

---

## Hardware Bill of Materials

* **Robot Controller:** GoPiGo3 Red Controller Board + Raspberry Pi 3B (`192.168.1.104`)
* **Sensor:** VL53L0X Time-of-Flight Distance Sensor (connected to GoPiGo I2C port)
* **Audio:** Jabra SPEAK 510 USB speakerphone (`card 2` / `plughw:2,0` over ALSA)
* **Smart Plug:** TP-Link Tapo Mini Smart Plug with Matter (`TP15(US)`, `192.168.1.105`)
* **Lighting:** AC outdoor floodlight / spotlight plugged into Tapo Smart Plug
* **Target:** Life-sized Skeleton positioned across the walkway

---

## Software & Protocol Design

1. **Local Zero-Cloud Relay (`tapo_relay.py`):**
   * Uses modern `tapo` Python bindings running under Python 3.12 (via `uv`) to natively handle TP-Link's encrypted **TPAP / SPAKE2+** local protocol.
   * Keeps an open session to the plug on port 80, exposing an ultra-fast local microservice on `http://127.0.0.1:8088/on` and `/off` with ~20ms response time.
2. **Main Scare Loop (`halloween_scare.py`):**
   * Runs under standard GoPiGo3 Python 3.7.
   * Continuously polls the I2C distance sensor.
   * Coordinates light switching, red eye status, audio playback via `aplay`, and cooldown.
3. **Headless Boot (`start_scare.sh`):**
   * Configured via `@reboot` in `crontab`.
   * Automatically boots up, starts the relay, and arms the machine with zero laptop or SSH intervention required outside.

---

## Quickstart & Commands

### 1. One-Command Deploy from Mac
```bash
bash deploy.sh 192.168.1.104
```

### 2. Live Log Monitoring
```bash
ssh pi@192.168.1.104 "tail -f /home/pi/scare.log"
```

### 3. Stop / Start Service
```bash
# Stop
ssh pi@192.168.1.104 "pkill -f halloween_scare.py"

# Start
ssh pi@192.168.1.104 "nohup python3 -u /home/pi/halloween_scare.py > /home/pi/scare.log 2>&1 &"
```

---

## License
MIT
