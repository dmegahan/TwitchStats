import requests
import csv
import threading
import time
import datetime
import os
import logging
import TwitchAPI
from TwitchGraph import Graph
import TwitchIRCBot
import config

import constants

logging.getLogger("requests").setLevel(logging.WARNING)

class TwitchThread(threading.Thread):
    def __init__(self, stream, csvPath, config):
        threading.Thread.__init__(self)
        #stream name
        self.stream = stream
        self.CSVfp = csvPath
        self._stopevent = threading.Event( )
        self.directory = csvPath
        self.config = config

    def toCSV(self, streamer_name, num_viewers, game):
        #get current time, format: Year-Month-Day Hour:Minute:Second
        exact_time = datetime.datetime.utcnow().strftime(self.config["DATE_TIME_FORMAT"])
        #check if directory exists
        if not os.path.exists(os.path.dirname(self.directory)):
            os.makedirs(os.path.dirname(self.directory))

        with open(self.directory, 'a') as fp:
            f_write = csv.writer(fp)
            f_write.writerow([num_viewers, game, exact_time])

    def run(self):
        #do the operations
        print self.stream + " thread started"
        logging.info(self.stream + " thread started")
        while not self._stopevent.isSet():
            [viewerNum, game] = TwitchAPI.getStreamInfo(self.stream)
            #stream is likely offline, end thread
            if game is config.STR_STREAM_OFFLINE:
                #error occured, wait some time and try again
                time.sleep(5)
            elif viewerNum is not None and game is not None:
                #everything went OK, add data to CSV
                #if a None is recieved, something broke so dont do anything
                timeout_checks = 0
                self.toCSV(self.stream, viewerNum, game)
            self._stopevent.wait(0.5)
        return

    def join(self, timeout=None):
        """ Stop the thread and wait for it to end. """
        self._stopevent.set( )
        threading.Thread.join(self, timeout)

"""
def main():
    parent = ParentThread()
    parent.setDaemon(False)
    parent.start()
    TwitchIRCBot.main()

main()"""