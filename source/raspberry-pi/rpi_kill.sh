echo "Killing server.."
kill -9 `cat server_pid.txt`
rm server_pid.txt

echo "Killing listener.."
kill -9 `cat listener_pid.txt`
rm listener_pid.txt

echo "Killing logger.."
kill -9 `cat logger_pid.txt`
rm logger_pid.txt
