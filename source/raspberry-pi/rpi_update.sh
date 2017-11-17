
# Copy scripts from the NUC to the Raspberry Pi

source config.sh

echo "Copying Python Code"
scp -r /home/bjornar/master-thesis/source/raspberry-pi/*.py pi@$RPI_IP:~/
echo "Pyhon Code Done"

echo "Copying Bash Scripts"
scp -r /home/bjornar/master-thesis/source/raspberry-pi/rpi_init.sh pi@$RPI_IP:~/
scp -r /home/bjornar/master-thesis/source/raspberry-pi/rpi_kill.sh pi@$RPI_IP:~/
scp -r /home/bjornar/master-thesis/source/raspberry-pi/config.sh pi@$RPI_IP:~/
echo "Bash Scripts Done"

echo "Copying HTML"
scp -r /home/bjornar/master-thesis/source/raspberry-pi/static/ pi@$RPI_IP:~/
echo "HTML Done"

echo "Raspberry Pi updated"
