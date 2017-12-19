# Startup script for the RPi web service

source config.sh

SERVER_LOG="$LOG_FOLDER/server.log"
LISTENER_LOG="$LOG_FOLDER/listener.log"

rm $SERVER_LOG
rm $LISTENER_LOG

# Meant to run from pi@raspberrypi_bjornapr:~
nohup python server.py > $SERVER_LOG 2>&1 &
echo $! > server_pid.txt # Save the pid for later destruction

nohup python listener.py > $LISTENER_LOG 2>&1 &
echo $! > listener_pid.txt # Save the pid for later destruction

echo "Logs in "$LOG_FOLDER

echo "server and listener up"


# Should start the following processes:
# - arduino control
# - machine learning
# - web interface
