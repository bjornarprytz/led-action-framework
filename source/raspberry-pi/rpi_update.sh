
# Copy scripts from the NUC to the Raspberry Pi

source config.sh

scp -r /home/bjornar/master-thesis/source/raspberry-pi pi@$RPI_IP:~/

echo "Raspberry Pi updated"
