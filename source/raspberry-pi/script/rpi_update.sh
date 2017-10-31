
# Copy scripts from the NUC to the Raspberry Pi

source config.sh

# Raspberry initiation script
cat rpi_init.sh | ssh pi@$RPI_IP "cat > rpi_init.sh"

echo "Raspberry Pi updated"
