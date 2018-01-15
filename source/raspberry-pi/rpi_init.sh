# Startup script for the RPi web service

source config.sh

SERVER_LOG="$LOG_FOLDER/server.log"
LISTENER_LOG="$LOG_FOLDER/listener.log"
LOGGER_LOG="$LOG_FOLDER/logger.log"

rm $SERVER_LOG
rm $LISTENER_LOG
rm $LOGGER_LOG

# Meant to run from pi@raspberrypi_bjornapr:~
nohup python server.py > $SERVER_LOG 2>&1 &
echo $! > server_pid.txt # Save the pid for later destruction

nohup python listener.py > $LISTENER_LOG 2>&1 &
echo $! > listener_pid.txt # Save the pid for later destruction

nohup python logger.py > $LOGGER_LOG 2>&1 &
echo $! > logger_pid.txt # Save the pid for later destruction

echo "Logs in "$LOG_FOLDER

echo "server, listener and logger up"


# Should start the following processes:
# - arduino control
# - machine learning
# - web interface
