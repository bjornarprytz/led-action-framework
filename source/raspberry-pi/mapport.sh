# Map a port from NUC to a port in the Raspberry Pi

source config.sh

echo "
Mapping localhost:$NUC_PORT to $RPI_IP:$RPI_PORT (Raspberry Pi)
"

ssh -L $NUC_PORT:localhost:$RPI_PORT $RPI_USERNAME@$RPI_IP


echo "Port Mapping Aborted. SSH tunnel must be persistent to work"
