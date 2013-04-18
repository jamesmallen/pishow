#!/bin/bash

PISHOW_DIR=/home/pi/pishow

while true; do
    echo "Starting pishow..."
    sudo $PISHOW_DIR/pishow.py
    
    echo "pishow quit. Attempting to restart (Ctrl-C to abort)"
    sleep 3
    
done
