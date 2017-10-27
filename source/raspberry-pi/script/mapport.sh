# Map a port from NUC to a port in the Raspberry Pi

source config.sh

ssh -L $NUC_PORT:localhost:$RPI_PORT $RPI_USERNAME@$RPI_IP
