kill -9 `cat server_pid.txt`
rm server_pid.txt

kill -9 `cat listener_pid.txt`
rm listener_pid.txt
