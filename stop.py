import subprocess

def stop_service():
    subprocess.Popen(['pkill', '-f', 'python main.py'])

stop_service()
