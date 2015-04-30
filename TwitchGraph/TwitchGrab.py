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

class ParentThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        #keeps track of streams that are offline, and checks on them periodically
        self.inactiveStreams = constants.STREAMERS[:]
        self.threadsAlive = []

    def status(self):
        print "Active streams: " + str(self.threadsAlive)
        print "Inactive streams: " + str(self.inactiveStreams)

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
            print stream + " is online!"
            logging.info(stream + " is online!")
            return True
        except (TypeError, ValueError, KeyError):
            #Error occured, check to see if stream is offline or if temp disconnect
            print "Error occurred checking online status."
            print streamResponse
            logging.debug(stream + " - Error occurred checking online status.")
            logging.debug(streamResponse)

    def run(self):
        while 1:
            date = datetime.datetime.utcnow().strftime("%d_%m_%Y")
            directory = constants.LOGS_FOLDER + date + ".log"
            if not os.path.exists(os.path.dirname(directory)):
                os.makedirs(os.path.dirname(directory))
            logging.basicConfig(filename=directory,
                                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                datefmt='%m/%d/%Y %H:%M:%S',
                                level=logging.DEBUG)
            #start the threads up
            for stream in self.inactiveStreams:
                if self.isOnline(stream):
                    t = TwitchThread(stream)
                    t.setDaemon(False)
                    t.start()
                    #start a thread and add it to another list, threadsAlive
                    self.inactiveStreams.remove(t.stream)
                    self.threadsAlive.append(t)

            #keep track of threads, if 1 ends, check up on it periodically
            for t in self.threadsAlive:
                #is the thread still alive?
                if not t.isAlive():
                    #thread ended, put into dead thread list
                    self.inactiveStreams.append(t.stream)
                    print t.stream + " died"
                    logging.info(t.stream + " died")
                    self.threadsAlive.remove(t)

            time.sleep(constants.PARENT_THREAD_SLEEP_TIME)


class TwitchThread(threading.Thread):
    def __init__(self, stream):
        threading.Thread.__init__(self)
        #stream name
        self.stream = stream
        self.CSVfp = datetime.datetime.utcnow().strftime(constants.GRAPH_FILE_FORMAT)
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
            time.sleep(30)
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
        timeout_checks = 0
        while not self._stopevent.isSet():
            [viewerNum, game] = self.getStreamInfo(self.stream)
            #stream is likely offline, end thread
            if game is constants.STR_STREAM_OFFLINE:
                if(timeout_checks > constants.TIMEOUT):
                    timeout_checks = 0
                    print self.stream + " Offline"
                    logging.info(self.stream + " Offline!")
                    self.toCSV(self.stream, constants.DEAD_THREAD_IDENTIFIER, constants.STR_STREAM_OFFLINE)
                    graph = Graph().createGraphFromCSV(self.directory)
                    break
                else:
                    print self.stream + " timeout checks: " + str(timeout_checks)
                    logging.info(self.stream + " timeout checks: " + str(timeout_checks))
                    timeout_checks = timeout_checks + 1
                    time.sleep(60)
            elif viewerNum is not None and game is not None:
                #everything went OK, add data to CSV
                #if a None is recieved, something broke so dont do anything
                timeout_checks = 0
                self.toCSV(self.stream, viewerNum, game)
            time.sleep(0.5)

        #Calculate the daily stats
        #swap the file paths

        json_file_path = constants.LOGS_FOLDER +
        return

    def join(self, timeout=None):
        """ Stop the thread and wait for it to end. """
        self._stopevent.set( )
        threading.Thread.join(self, timeout)

def main():
    parent = ParentThread()
    parent.setDaemon(False)
    parent.start()
    TwitchIRCBot.main()

main()