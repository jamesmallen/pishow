#!/bin/bash

scp -p * pi@192.168.1.137:~/pishow/
ssh -t pi@192.168.1.137 sudo /home/pi/pishow/run.sh