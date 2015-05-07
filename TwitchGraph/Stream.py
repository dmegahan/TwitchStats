import datetime
import os
import threading
import logging
import requests
import time
from JsonEditor import JsonEditor
from Statistics import Statistics
from TwitchGrab import TwitchThread
from TwitchGraph import Graph
from TwitchIRCBot import TwitchIRCBot
import config
import constants

__author__ = 'Danny'

class Stream(threading.Thread):
    def __init__(self, stream):
        threading.Thread.__init__(self)
        self.stream = stream
        self.IRCBot = None
        self.GrabBot = None
        self.config = config.config["default"]

        self.CSVfp = ""
        self.JSONfp = ""
        self.LOGfp = ""
        self.globalPath = ""

        self.timeout = 0

        self.activeThreads = []

    def getRecentStream(self):
        #this function will check to see if there is a recent file, from a stream session that may still be going
        #this function provides continuation of a stream data grab even if you restart the program
        #we will check for recent csv files, if it is within a set number of minutes, that is recent and we will
        #continue adding data to that file
        max_mtime = 0
        last_modified_file = ""
        dir = "./data/" + self.stream + self.config["CSV_FOLDER"]
        for dirname, subdirs, files in os.walk(dir):
            for fname in files:
                full_path = os.path.join(dirname, fname)
                mtime = os.stat(full_path).st_mtime
                if mtime > max_mtime:
                    max_mtime = mtime
                    last_modified_file = fname

        current_time = time.time()
        difference = current_time - max_mtime
        if difference < self.config["RECONNECT_TIME"]:
            print "We're trying to reconnect!"
            return last_modified_file.split(".")[0]
        else:
            return None

    def initFileNames(self):
        date = datetime.datetime.utcnow()
        parent_dir = './data/' + self.stream
        recent_file_name = self.getRecentStream()
        if recent_file_name is not None:
            print self.stream + " is continuing!"
            self.CSVfp = parent_dir + self.config["CSV_FOLDER"] + recent_file_name + ".csv"
            self.JSONfp = parent_dir + self.config["STATS_FOLDER"] + recent_file_name + ".json"
            self.LOGfp = parent_dir + self.config["LOGS_FOLDER"] + recent_file_name + ".log"
        else:
            self.CSVfp = date.strftime(parent_dir + self.config["CSV_FOLDER"] + self.config["GRAPH_FILE_FORMAT"])
            self.JSONfp = date.strftime(parent_dir + self.config["STATS_FOLDER"] + self.config["JSON_FILE_FORMAT"])
            self.LOGfp = date.strftime(parent_dir + self.config["LOGS_FOLDER"] + self.config["CHAT_LOG_FILE_FORMAT"])
        self.globalPath = parent_dir + self.config["STATS_FOLDER"] + self.stream + ".json"

        if not os.path.exists(os.path.dirname(self.CSVfp)):
            os.makedirs(os.path.dirname(self.CSVfp))
        if not os.path.exists(os.path.dirname(self.JSONfp)):
            os.makedirs(os.path.dirname(self.JSONfp))
        if not os.path.exists(os.path.dirname(self.LOGfp)):
            os.makedirs(os.path.dirname(self.LOGfp))
        if not os.path.exists(os.path.dirname(self.globalPath)):
            os.makedirs(os.path.dirname(self.globalPath))

        directory = './logs/' + date.strftime(self.config["LOG_FILE_FORMAT"])
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

    def recordStats(self):
        jsonFile = JsonEditor(self.JSONfp, "")
        stats = Statistics(self.CSVfp, self.JSONfp, self.LOGfp, self.globalPath, self.config)
        dailyStats = stats.doDaily()
        jsonFile.toJSON(dailyStats)



    def run(self):
        while 1:
            if self.isOnline(self.stream):
                #start the bots up
                if self.GrabBot is None and self.IRCBot is None:
                    #initialize the dates and filepaths
                    self.initFileNames()

                    self.GrabBot = TwitchThread(self.stream, self.CSVfp, self.config)
                    self.GrabBot.setDaemon(False)
                    self.GrabBot.start()

                    self.IRCBot = TwitchIRCBot(self.stream, self.JSONfp, self.LOGfp, self.config)
                    self.IRCBot.setDaemon(False)
                    self.IRCBot.start()
            else:
                if self.GrabBot is not None and self.IRCBot is not None:
                    #start timing out
                    if self.timeout > self.config["TIMEOUT"]:
                        print "stream is offline. Ending threads."
                        #do end of stream
                        self.GrabBot.toCSV(self.stream, config.DEAD_THREAD_IDENTIFIER, config.STR_STREAM_OFFLINE)
                        g = Graph(self.config)
                        g.createGraphFromCSV(self.CSVfp)
                        g.createGraphFromJson(self.JSONfp)

                        self.recordStats()

                        self.GrabBot.join()
                        self.IRCBot.join()
                        self.GrabBot = None
                        self.IRCBot = None
                    else:
                        print self.stream + " timing out: " + str(self.timeout)
                        self.timeout += 1

            time.sleep(self.config["PARENT_THREAD_SLEEP_TIME"])

def main():
    inactiveStreams = config.STREAMERS[:]
    activeStreams = []
    while 1:
        for stream in inactiveStreams[:]:
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