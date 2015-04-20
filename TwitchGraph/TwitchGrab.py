import requests
import csv
import threading
import time
import datetime
import os
import logging
from TwitchGraph import Graph

import constants

class ParentThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        #keeps track of streams that are offline, and checks on them periodically
        self.inactiveStreams = constants.STREAMERS
        self.threadsAlive = []

    def isOnline(self, stream):
        #check if a stream is online by seeing if the object[stream] returns null
        STREAM_REQUEST = "https://api.twitch.tv/kraken/streams/" + stream
        streamResponse = None
        try:
           streamResponse = requests.get(STREAM_REQUEST)
        except requests.exceptions.ConnectionError:
            print "request failure: " + STREAM_REQUEST
            #get stream info from streamResponse
        try:
            streamObj = streamResponse.json()
            if streamObj['stream'] is None:
                return False
            print stream + " is online!"
            return True
        except (TypeError, ValueError, KeyError):
            #Error occured, check to see if stream is offline or if temp disconnect
            print "Error occurred checking online status."
            print streamResponse

    def run(self):
        while 1:
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
                    self.threadsAlive.remove(t)

            time.sleep(constants.PARENT_THREAD_SLEEP_TIME)


class TwitchThread(threading.Thread):
    def __init__(self, stream):
        threading.Thread.__init__(self)
        #stream name
        self.stream = stream
        date = datetime.datetime.utcnow().strftime("%d_%m_%Y")
        self.CSVfp = date + ".csv"
        self.directory = './data/' + stream + '/' + self.CSVfp

    def toCSV(self, streamer_name, num_viewers, game):
        #get current time, format: Year-Month-Day Hour:Minute:Second
        exact_time = datetime.datetime.utcnow().strftime("%H:%M:%S")
        directory = './data/' + streamer_name + '/' + self.CSVfp
        #check if directory exists
        if not os.path.exists(os.path.dirname(directory)):
            os.makedirs(os.path.dirname(directory))

        with open(directory, 'a') as fp:
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
            return [None, None]

        #get stream info from streamResponse
        streamObj = None
        try:
            streamObj = streamResponse.json()
            #stream object returned null, so stream is likely offline
            if streamObj['stream'] is None:
                #return nulls so that the thread will be exited
                return [constants.DEAD_THREAD_IDENTIFIER, constants.STR_STREAM_OFFLINE]
            viewerNum = streamObj['stream']['viewers']
            game = streamObj['stream']['game']
        except (TypeError, ValueError, KeyError):
            #Error occured, temp disconnect
            print "Error occurred getting stream information on " + stream
            print streamResponse
            #something messed up, dont add anything to csv
            return [None, None]

        #return our relevant data
        return [viewerNum, game]

    def run(self):
        #do the operations
        print self.stream + " thread started"
        while 1:
            [viewerNum, game] = self.getStreamInfo(self.stream)
            #stream is likely offline, end thread
            if game is constants.STR_STREAM_OFFLINE:
                print self.stream + " Offline"
                self.toCSV(self.stream, constants.DEAD_THREAD_IDENTIFIER, constants.STR_STREAM_OFFLINE)
                graph = Graph(self.directory)
                break
            elif viewerNum is not None and game is not None:
                #everything went OK, add data to CSV
                #if a None is recieved, something broke so dont do anything
                self.toCSV(self.stream, viewerNum, game)
            time.sleep(0.5)
        return

def main():
    parent = ParentThread()
    parent.setDaemon(False)
    parent.start()

main()