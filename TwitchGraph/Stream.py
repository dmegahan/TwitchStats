import datetime
import os
import threading
import logging
import requests
import time
from TwitchGrab import TwitchThread
from TwitchGraph import Graph
from TwitchIRCBot import TwitchIRCBot
import constants

__author__ = 'Danny'

class Stream(threading.Thread):
    def __init__(self, stream):
        threading.Thread.__init__(self)
        self.stream = stream
        self.IRCBot = None
        self.GrabBot = None

        self.CSVfp = ""
        self.JSONfp = ""
        self.LOGfp = ""

        self.timeout = 0

        self.activeThreads = []

    def initFileNames(self):
        print self.stream + " initialized filepaths"
        date = datetime.datetime.utcnow()
        self.CSVfp = date.strftime(constants.GRAPH_FILE_FORMAT)
        self.JSONfp = date.strftime(constants.JSON_FILE_FORMAT)
        self.LOGfp = date.strftime(constants.CHAT_LOG_FILE_FORMAT)

        directory = constants.LOGS_FOLDER + self.LOGfp
        if not os.path.exists(os.path.dirname(directory)):
            os.makedirs(os.path.dirname(directory))
        logging.basicConfig(filename=directory,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %H:%M:%S',
                            level=logging.DEBUG)

    def isOnline(self, stream):
        #check if a stream is online by seeing if the object[stream] returns null
        STREAM_REQUEST = "https://api.twitch.tv/kraken/streams/" + stream
        streamResponse = None
        try:
           streamResponse = requests.get(STREAM_REQUEST)
        except requests.exceptions.ConnectionError:
            #print "request failure: " + STREAM_REQUEST
            logging.debug("request failure: " + STREAM_REQUEST)
            #get stream info from streamResponse
            return False
        try:
            streamObj = streamResponse.json()
            if streamObj['stream'] is None:
                return False
            #print stream + " is online!"
            #logging.info(stream + " is online!")
            return True
        except (TypeError, ValueError, KeyError):
            #Error occured, check to see if stream is offline or if temp disconnect
            print "Error occurred checking online status."
            print streamResponse
            logging.debug(stream + " - Error occurred checking online status.")
            logging.debug(streamResponse)
        return False

    def run(self):
        while 1:
            if self.isOnline(self.stream):
                #start the bots up
                if self.GrabBot is None and self.IRCBot is None:
                    #initialize the dates and filepaths
                    self.initFileNames()

                    self.GrabBot = TwitchThread(self.stream, self.CSVfp)
                    self.GrabBot.setDaemon(False)
                    self.GrabBot.start()

                    self.IRCBot = TwitchIRCBot(self.stream, self.JSONfp, self.LOGfp)
                    self.IRCBot.setDaemon(False)
                    self.IRCBot.start()
            else:
                if self.GrabBot is not None and self.IRCBot is not None:
                    if self.GrabBot.is_alive and self.IRCBOt.is_alive:
                        #start timing out
                        if self.timeout > constants.TIMEOUT:
                            print "stream is offline. Ending threads."
                            #do end of stream
                            self.GrabBot.toCSV(self.stream, constants.DEAD_THREAD_IDENTIFIER, constants.STR_STREAM_OFFLINE)
                            Graph().createGraphFromCSV(self.CSVfp)
                            Graph().createGraphFromJson(self.JSONfp)
                            self.GrabBot.join()
                            self.IRCBot.join()

                            self.GrabBot = None
                            self.IRCBot = None
                        else:
                            ++self.timeout

            time.sleep(constants.PARENT_THREAD_SLEEP_TIME)

def main():
    inactiveStreams = constants.STREAMERS[:]
    activeStreams = []
    while 1:
        for stream in inactiveStreams:
            s = Stream(stream)
            s.setDaemon(False)
            s.start()
            activeStreams.append(s)
            inactiveStreams.remove(s.stream)
            #keep track of threads, if 1 ends, check up on it periodically
        for stream in activeStreams:
            #is the thread still alive?
            if not stream.is_alive:
                #thread ended, put into dead thread list
                inactiveStreams.append(stream.stream)
                print stream.stream + " died"
                logging.info(stream.stream + " died")
                activeStreams.remove(stream)

        time.sleep(60)

main()