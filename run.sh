#!/bin/bash

PISHOW_DIR=/home/pi/pishow

while true; do
    echo "Killing any old processes..."
    kill -9 $(ps aux | grep '[p]ishow.py' | awk '{print $2}')
    killall omxplayer omxplayer.bin
    
    echo "Starting pishow..."
    sudo $PISHOW_DIR/pishow.py
    
    # if we hit this line, we exited - try showing USB missing image
    sudo killall fbi
    sudo fbi -T 1 -noverbose -a $PISHOW_DIR/missing.png
    
    # echo to stdout just in case
    echo "pishow quit. Attempting to restart in 5 seconds... (Ctrl-C to abort)"
    sleep 5
    
done
