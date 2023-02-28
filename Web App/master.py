import paramiko
import sys
from time import sleep

# This script is used to communicate with the master inside the VM

if len(sys.argv) == 1:
    exit(0)

HOST = "localhost"
USERNAME = "comnetsemu"
PASSWORD = "comnetsemu"

MASTER_PATH = "The path of the master inside the VM"

command = sys.argv[1]
command = f"python3 {MASTER_PATH} {command}"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, port=2222)
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)

while not ssh_stdout.channel.eof_received:
    sleep(1)

result = ssh_stdout.read().decode()

ssh_stdin.close()
ssh_stdout.close()
ssh_stderr.close()

ssh.close()

print(result)
