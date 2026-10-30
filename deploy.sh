#!/usr/bin/env bash
# halloween-scare-machine: One-shot deployment from MacBook to GoPiGo3
set -e

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_HOST="${1:-192.168.1.104}"
ROBOT_USER="pi"

echo "=========================================================="
echo "  Deploying Halloween Scare Machine to GoPiGo3 ($TARGET_HOST)"
echo "=========================================================="

python3 - << EOF
import paramiko, sys, os

host = "$TARGET_HOST"
user = "$ROBOT_USER"
source = "$SOURCE_DIR"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(host, username=user, password='robots1234', timeout=5)
except Exception:
    ssh.connect(host, username=user, password='robotsrule', timeout=5)

sftp = ssh.open_sftp()
print("[1/3] Uploading scripts...")
for script in ['halloween_scare.py', 'tapo_relay.py', 'start_scare.sh']:
    src_path = os.path.join(source, script)
    if os.path.exists(src_path):
        sftp.put(src_path, f'/home/pi/{script}')
        ssh.exec_command(f'chmod +x /home/pi/{script}')
        print(f"  - {script}")

print("[2/3] Uploading audio assets...")
for audio in ['ghost_moan_15s.wav', 'bones_rattling_30s.wav']:
    src_path = os.path.join(source, 'audio', audio)
    if os.path.exists(src_path):
        sftp.put(src_path, f'/home/pi/{audio}')
        print(f"  - {audio}")

sftp.close()

print("[3/3] Restarting live scare service on robot...")
ssh.exec_command('pkill -f halloween_scare.py 2>/dev/null || true')
ssh.exec_command('nohup python3 -u /home/pi/halloween_scare.py > /home/pi/scare.log 2>&1 &')
ssh.close()
print("==========================================================")
print("[SUCCESS] Halloween Scare Machine deployed and armed!")
print("==========================================================")
EOF
