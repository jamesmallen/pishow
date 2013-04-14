#!/usr/bin/python


from pishow import OMXPlayer
import os
import time
import signal
import sys
import atexit


@atexit.register
def kill_subprocesses():
    del cur
    del next


testfiles = ['/media/usb/Promo Gray BG.mp4',
             '/media/usb/Promo Creme BG.mp4',]




idx = 0
next = None
cur = None
old = None


while True:
    if not cur:
        print("loading {0}".format(testfiles[idx]))
        cur = OMXPlayer(track = testfiles[idx])
    
    cur.play()
    
    time.sleep(2)
    
    del old
    
    time.sleep(6)
    
    idx += 1
    idx %= len(testfiles)
    
    print("loading {0}".format(testfiles[idx]))
    next = OMXPlayer(track = testfiles[idx])
    
    #cur.wait()
    time.sleep(3)
    
    cur.pause()
    
    old = cur
    cur = next


foo = OMXPlayer()

foo.load('/media/usb/00003_Test Video 1080p.m4v', startpaused=True)

bar = OMXPlayer()
bar.load('/media/usb/00003_Test Video 1080p.m4v', startpaused=True)

foo.play()
print("just played")
foo.wait()

bar.play()
print("just played bar")

#foo.wait()
