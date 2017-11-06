# Startup script for the RPi web service

rm server.log
rm listener.log

# Meant to run from pi@raspberrypi_bjornapr:~
nohup python server.py > server.log 2>&1 &
echo $! > server_pid.txt # Save the pid for later destruction

nohup python listener.py > listener.log 2>&1 &
echo $! > listener_pid.txt # Save the pid for later destruction


echo "server and listener up"


# Should start the following processes:
# - arduino control
# - machine learning
# - web interface
