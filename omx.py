import os, subprocess, signal
import time
import copy
import uuid
import logging


class OMXPlayer:
    __defaults = {
        'proc': None,
        #'opts': ['-ohdmi'],
        'opts': [],
        'fifo': '/tmp/omxcmd',
        
        #'terminate_timeout': 0.2
    }
    
    def __init__(self, track = None, opts = None, fifo = None):
        self.__dict__ = copy.deepcopy(self.__defaults)
        
        myuuid = str(uuid.uuid4())
        
        self.track = track or self.track
        self.opts = opts or self.opts
        self.fifo = fifo or self.fifo + myuuid
        
        if track:
            self.load(track, startpaused=True)
    
    def __del__(self):
        self.__stop_child()
    
    def __start_child(self, track):
        assert self.proc == None
        
        logging.debug("setting up fifo {0}".format(self.fifo))
        if os.path.exists(self.fifo):
            logging.debug("(first removing old fifo)")
            os.remove(self.fifo)
        
        os.mkfifo(self.fifo)
        
        self.proc = subprocess.Popen('omxplayer {0} "{1}" <"{2}"'.format(
                                     ' '.join(self.opts), track, self.fifo),
                                     shell=True,
                                     preexec_fn=os.setsid)
        
        
        logging.debug("omx child pid: {0}".format(self.proc.pid))
        
        # wait until child has started before sending commands
        while self.proc.poll() != None:
            logging.debug("waiting for omx child to start...")
            time.sleep(0.1)
        
        logging.debug("omx child started")
        
    def __stop_child(self):
        logging.debug("stopping omx child...")
        if self.proc:
            # kill entire process group
            os.killpg(self.proc.pid, signal.SIGTERM)
            self.proc = None
        if os.path.exists(self.fifo):
            logging.debug("removing fifo {0}".format(self.fifo))
            os.remove(self.fifo)
            
    def __isrunning(self):
        return self.proc != None and self.proc.poll() is None
    
    
    def __send_control(self, c):
        #logging.debug("sending control {0}".format(c))
        
        # attempt to open fifo nonblocking to prevent freezing
        # TODO: wait a little bit/try again? debug cause of vid not playing
        
        try:
            fd = os.open(self.fifo, os.O_WRONLY | os.O_NONBLOCK)
        except OSError:
            logging.error("Unable to open fifo {0} for writing".format(self.fifo))
        else:
            if fd > 0:
                # only write if we get a valid fd (<=0 indicates error)
                try:
                    os.write(fd, c)
                except OSError:
                    logging.error("error writing to fifo {0}".format(self.fifo))
                finally:
                    os.close(fd)
        
        
    def load(self, path, startpaused = False):
        self.__start_child(path)
        
        # wait just a tad...
        time.sleep(0.1)
        
        if startpaused:
            logging.debug('starting paused')
            self.__send_control('p')
            self.paused = True
        else:
            # send a period to open the fifo and get things started
            self.__send_control('.')
            self.paused = False
                
    
    def play(self):
        logging.debug('play')
        if self.paused:
            self.__send_control('p')
            self.paused = False


    def pause(self):
        logging.debug('pause')
        if not self.paused:
            self.__send_control('p')
            self.paused = True
    
    def quit(self):
        self.__send_control('q')


    def wait(self):
        if self.__isrunning():
            self.proc.wait()
            
        else:
            logging.debug("wait called, but process already complete")
