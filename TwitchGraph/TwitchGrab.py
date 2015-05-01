import requests
import csv
import threading
import time
import datetime
import os
import logging
from TwitchGraph import Graph
import TwitchIRCBot

import constants

logging.getLogger("requests").setLevel(logging.WARNING)

class TwitchThread(threading.Thread):
    def __init__(self, stream, csvPath):
        threading.Thread.__init__(self)
        #stream name
        self.stream = stream
        self.CSVfp = csvPath
        self._stopevent = threading.Event( )
        self.directory = './data/' + stream + '/' + self.CSVfp

    def toCSV(self, streamer_name, num_viewers, game):
        #get current time, format: Year-Month-Day Hour:Minute:Second
        exact_time = datetime.datetime.utcnow().strftime(constants.TIME_FORMAT)
        #check if directory exists
        if not os.path.exists(os.path.dirname(self.directory)):
            os.makedirs(os.path.dirname(self.directory))

        with open(self.directory, 'a') as fp:
            f_write = csv.writer(fp)
            f_write.writerow([num_viewers, game, exact_time])

    def getStreamInfo(self, stream):
        #API only shows the first 25 followed streams by default
        #defaults: offset = 0, limit = 25
        #https://github.com/justintv/Twitch-API/blob/master/v3_resources/follows.md#get-usersuserfollowschannels

        #request stream data
        STREAM_REQUEST = "https://api.twitch.tv/kraken/streams/" + stream
        streamResponse = None
        try:
           streamResponse = requests.get(STREAM_REQUEST)
        except requests.exceptions.ConnectionError:
            print "request failure: " + STREAM_REQUEST
            logging.debug(stream + " - request failure: " + STREAM_REQUEST)
            return [None, None]

        #get stream info from streamResponse
        streamObj = None
        try:
            #we will continue to check for a valid streamObj until 5 minutes are up, that's our timeout
            streamObj = streamResponse.json()
            #stream object returned null, so stream is likely offline
            if streamObj['stream'] is None:
                #return nulls so that the thread will be exited
                #stream is offline, or we didn't receive anything from twitch
                return [constants.DEAD_THREAD_IDENTIFIER, constants.STR_STREAM_OFFLINE]
            viewerNum = streamObj['stream']['viewers']
            game = streamObj['stream']['game']
        except (TypeError, ValueError, KeyError):
            #Error occured, temp disconnect
            print "Error occurred getting stream information on " + stream
            print streamResponse
            logging.debug(stream + " - Error occurred getting stream information on " + stream)
            logging.debug(streamResponse)
            #something messed up, dont add anything to csv
            return [None, None]

        #return our relevant data
        return [viewerNum, game]

    def run(self):
        #do the operations
        print self.stream + " thread started"
        logging.info(self.stream + " thread started")
        while not self._stopevent.isSet():
            [viewerNum, game] = self.getStreamInfo(self.stream)
            #stream is likely offline, end thread
            if game is constants.STR_STREAM_OFFLINE:
                #error occured, wait some time and try again
                time.sleep(5)
            elif viewerNum is not None and game is not None:
                #everything went OK, add data to CSV
                #if a None is recieved, something broke so dont do anything
                timeout_checks = 0
                self.toCSV(self.stream, viewerNum, game)
            time.sleep(0.5)
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