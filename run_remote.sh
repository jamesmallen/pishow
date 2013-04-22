#!/bin/bash

REMOTE_ADDR=192.168.2.2

ssh -t pi@$REMOTE_ADDR sudo /home/pi/pishow/unlock.sh
scp -p * pi@$REMOTE_ADDR:~/pishow/
ssh -t pi@$REMOTE_ADDR sudo /home/pi/pishow/relock.sh
ssh -t pi@$REMOTE_ADDR sudo /home/pi/pishow/run.sh
