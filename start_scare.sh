#!/bin/bash
sleep 10
# Kill any existing instances
pkill -f halloween_scare.py 2>/dev/null || true
python3 -u /home/pi/halloween_scare.py >> /home/pi/scare.log 2>&1 &
