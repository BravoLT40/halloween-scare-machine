#!/bin/bash
sleep 8
pkill -f tapo_relay.py 2>/dev/null || true
pkill -f halloween_scare.py 2>/dev/null || true

# Start Tapo relay microservice using the dedicated Python 3.12 environment
nohup /home/pi/tapo_env/bin/python /home/pi/tapo_relay.py > /home/pi/relay.log 2>&1 &
sleep 2

# Start Halloween scare main loop
nohup python3 -u /home/pi/halloween_scare.py > /home/pi/scare.log 2>&1 &
