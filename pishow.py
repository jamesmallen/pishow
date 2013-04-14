#!/usr/bin/python

from __future__ import division

import os
import pygame
import time
import random
import math

import subprocess
import signal
import logging
import re
import copy
import uuid
import fcntl

from omx import OMXPlayer


logging.basicConfig(level=logging.DEBUG)


media_path = '/media/UNTITLED'

# Files should be named in the following format:
# Content_AAA_BBB.jpg
# AAA is used to determine the order the files are played in
# BBB is used to determine how many seconds a file should appear

# For example, a file named Content_001_014.jpg would be the first image
# to appear, and it would stay on screen for 14 seconds.




    
        
        
    


class SSPic:

    def __init__(self, path, letterbox = True):
        self.path = path
        self.cached = False
        self.img = None
        self.letterbox = letterbox

    def cache(self):
        "Caches the image"
        self.img = self.scale_img(pygame.image.load(self.path),
                                  self.letterbox)
        self.cached = True

    def show(self, screen):
        "Shows the image"
        if (not self.cached):
            self.cache()

        screen.fill((0, 0, 0))
        screen.blit(self.img, (0,0))
        pygame.display.update()



    def scale_img(self, img, letterbox = True):
        "Scales image to fill screen."
        # Based on code from http://uihacker.blogspot.com/2012/10/javascript-letterbox-pillowbox-or-crop.html
        
        img = img.convert(32)
        
        target_w = pygame.display.Info().current_w
        target_h = pygame.display.Info().current_h
        
        target = pygame.Surface((target_w, target_h), depth=32)
        # target.fill((0, 0, 0))
        
        img_w = img.get_width()
        img_h = img.get_height()
        
        ratio_w = target_w / img_w
        ratio_h = target_h / img_h
        
        if ratio_w > ratio_h:
            shorter_ratio = ratio_h
            longer_ratio = ratio_w
        else:
            shorter_ratio = ratio_w
            longer_ratio = ratio_h
        
        if letterbox:
            resized_w = int(math.ceil(img_w * shorter_ratio))
            resized_h = int(math.ceil(img_h * shorter_ratio))
        else:
            resized_w = int(math.ceil(img_w * longer_ratio))
            resized_h = int(math.ceil(img_h * longer_ratio))
        
        offset_x = int(math.ceil((target_w - resized_w) * 0.5))
        offset_y = int(math.ceil((target_h - resized_h) * 0.5))
        
        img = pygame.transform.smoothscale(img, (resized_w, resized_h))
        target.blit(img, (offset_x, offset_y))
        
        return target



class SSVid:
    
    def __init__(self, path):
        self.path = path
        self.cached = False

    def cache(self):
        "Caches the video"
        self.img = self.scale_img(pygame.image.load(self.path),
                                  self.letterbox)
        self.cached = True

    def show(self, screen):
        "Shows the image"
        if (not self.cached):
            self.cache()

        screen.fill((0, 0, 0))
        screen.blit(self.img, (0,0))
        pygame.display.update()




class Slideshow:
    screen = None
    images = None
    watch_dir = media_path
    omx_exts = ['mpg', 'm4v', 'mov', 'mkv', 'avi']
    internal_exts = ['jpg', 'png', 'gif', 'bmp', 'pcx', 'tga', 'tif']
    default_duration = 5
    
    def __init__(self, watch_dir = None):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            logging.info("I'm running under X display = {0}".format(disp_no))
        
        # Check which frame buffer drivers are available
        # Start with fbcon since directfb hangs with composite output
        drivers = ['fbcon', 'directfb', 'svgalib']
        found = False
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                logging.info('Driver: {0} failed.'.format(driver))
                continue
            found = True
            logging.info("Video initialized using driver {0}".format(driver))
            break
        
        if not found:
            raise Exception('No suitable video driver found!')
        
        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        logging.info("Framebuffer size: %d x %d" % (size[0], size[1]))
        logging.debug(pygame.display.Info())
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        
        # Clear the screen to start
        self.screen.fill((0, 0, 0))
        
        # Initialise font support
        pygame.font.init()
        
        # Disable the mouse
        pygame.mouse.set_visible(False)
        
        # Render the screen
        pygame.display.update()
        
        # Initialize the images list
        self.images = []
        
        self.watch_dir = watch_dir or self.watch_dir
        
        self.populate_images()
    
    
    def populate_images(self):
        self.images = []
        files = os.listdir(self.watch_dir)
        for f in files:
            root, ext = os.path.splitext(f)
            if root.startswith('.'):
                # skip "hidden" files
                logging.debug("Skipping hidden file {0}".format(f))
                continue
            ext = ext.lower().strip('.')
            if ext in self.omx_exts or ext in self.internal_exts:
                logging.info("Adding file {0}".format(f))
                self.images.append(os.path.join(self.watch_dir, f))
            else:
                logging.debug("{0} doesn't match (ext: {1})".format(f, ext))
        
        # sort by name
        self.images.sort()
    
    
    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."
    
    
    def run(self):
        while True:
            for f in self.images:
                root, ext = os.path.splitext(f)
                ext = ext.lower().strip('.')
                
                if ext in self.omx_exts:
                    logging.info("Playing {0} using omxplayer".format(f))
                    
                    self.screen.fill((0, 0, 0))
                    pygame.display.update()
                    
                    subprocess.call(['omxplayer', '-o', 'hdmi', f])
                    
                    self.screen.fill((0, 0, 0))
                    pygame.display.update()
                
                elif ext in self.internal_exts:
                    logging.info("Showing {0}".format(f))
                    duration_match = re.search(r'[0-9]*$', root)
                    if not duration_match:
                        logging.debug("No duration found for {0}. Using default duration of {1}".format(
                            f, self.default_duration))
                        duration = self.default_duration
                    else:
                        duration = int(duration_match.group())
                    
                    next_img = SSPic(f)
                    next_img.cache()
                    
                    next_img.show(self.screen)
                    
                    time.sleep(duration)
        




def main():

    # Create an instance of the PyScope class
    show = Slideshow()


    # Test video
    #show.screen.fill((0,0,255))
    #pygame.display.update()
    #subprocess.call(['omxplayer', '-o', 'hdmi', '/media/usbdisk/Test Video.m4v'])

    #time.sleep(5)

    show.run()



if __name__ == '__main__':
    main()
