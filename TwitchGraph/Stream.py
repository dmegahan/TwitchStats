import datetime
import os
import threading
import logging
import sys
import requests
import time
from JsonEditor import JsonEditor
from Statistics import Statistics
import TwitchAPI
from TwitchBot import TwitchThread
from TwitchGraph import Graph
from TwitchIRCBot import TwitchIRCBot
import config
import constants

__author__ = 'Danny'

#A Stream object is the encompassing object that holds both the IRCBot and the GrabBot(Which is a bot that collects
#stream data). The Stream object keeps track
class Stream(threading.Thread):
    def __init__(self, stream):
        threading.Thread.__init__(self)
        self.stream = stream
        self.IRCBot = None
        self.GrabBot = None

        self.config = config.config["default"]
        #we need to see if the streamer has a custom config
        for configs in config.config_users:
            for user in config.config_users[configs]:
                if user == self.stream:
                    #we use this config!
                    self.config = config.config[configs]
                    #break out of both loops, we cant waste time
                    break
            else:
                continue
            break

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
            #we check to see if a file is in "progress". This is so we dont create a new file if the stream got
            #disconnected, on our end or theirs.
            print self.stream + " is continuing!"
            self.CSVfp = parent_dir + self.config["CSV_FOLDER"] + recent_file_name + ".csv"
            self.JSONfp = parent_dir + self.config["STATS_FOLDER"] + recent_file_name + ".json"
            self.LOGfp = parent_dir + self.config["LOGS_FOLDER"] + recent_file_name + ".log"
        else:
            #else we start a new, fresh file
            self.CSVfp = date.strftime(parent_dir + self.config["CSV_FOLDER"] + self.config["GRAPH_FILE_FORMAT"])
            self.JSONfp = date.strftime(parent_dir + self.config["STATS_FOLDER"] + self.config["JSON_FILE_FORMAT"])
            self.LOGfp = date.strftime(parent_dir + self.config["LOGS_FOLDER"] + self.config["CHAT_LOG_FILE_FORMAT"])
        self.globalPath = parent_dir + self.config["STATS_FOLDER"] + self.stream + ".json"

        #create the files if they dont exist
        if not os.path.exists(os.path.dirname(self.CSVfp)):
            os.makedirs(os.path.dirname(self.CSVfp))
        if not os.path.exists(os.path.dirname(self.JSONfp)):
            os.makedirs(os.path.dirname(self.JSONfp))
        if not os.path.exists(os.path.dirname(self.LOGfp)):
            os.makedirs(os.path.dirname(self.LOGfp))
        if not os.path.exists(os.path.dirname(self.globalPath)):
            os.makedirs(os.path.dirname(self.globalPath))

        #add a file for our logs so we can bugfix if we need to
        directory = './logs/' + date.strftime(config.LOG_FILE_FORMAT)
        if not os.path.exists(os.path.dirname(directory)):
            os.makedirs(os.path.dirname(directory))
        logging.basicConfig(filename=directory,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %H:%M:%S',
                            level=logging.DEBUG)

    def recordStats(self):
        #create all of our stats for the stream, is run after the stream is over
        jsonFile = JsonEditor(self.JSONfp, self.globalPath)
        stats = Statistics(self.stream, self.CSVfp, self.JSONfp, self.LOGfp, self.globalPath, self.config)
        dailyStats = stats.doDaily()
        jsonFile.toJSON(dailyStats)
        print self.stream + ": Tally Emotes started!"
        stats.tallyEmotes()
        print self.stream + ": End of stream tasks finished!"

    def run(self):
        while 1:
            #if stream is online
            if TwitchAPI.isOnline(self.stream):
                #start the bots up
                if self.GrabBot is None and self.IRCBot is None:
                    #initialize the dates and filepaths
                    self.initFileNames()

                    #check to see if the config specifies whether the twitch bot and irc bot should be on or off (t/f)
                    if self.config["TWITCH_BOT"] is True:
                        print("Started bot: " + self.stream);
                        self.GrabBot = TwitchThread(self.stream, self.CSVfp, self.config)
                        self.GrabBot.setDaemon(False)
                        #start the GrabBot up
                        self.GrabBot.start()

                    if self.config["IRC_BOT"] is True:
                        self.IRCBot = TwitchIRCBot(self.stream, self.JSONfp, self.LOGfp, self.config, self.globalPath)
                        self.IRCBot.setDaemon(False)
                        #start the IRCBot up
                        self.IRCBot.start()
            else:
                #if something is active
                if self.GrabBot is not None or self.IRCBot is not None:
                    #start timing out
                    if self.timeout > self.config["TIMEOUT"]:
                        print "stream is offline. Ending threads."
                        #do end of stream
                        if self.GrabBot is not None:
                            print "Ending GrabBot thread"
                            self.GrabBot.toCSV(self.stream, config.DEAD_THREAD_IDENTIFIER, config.STR_STREAM_OFFLINE)
                            g = Graph(self.config)
                            g.createGraphFromCSV(self.CSVfp)
                            self.GrabBot.join()
                            self.GrabBot = None

                        if self.IRCBot is not None:
                            print "Ending IRCBot thread"
                            g.createGraphFromJson(self.JSONfp)
                            if self.config["ALWAYS_ONLINE"] is not True:
                                self.IRCBot.join()
                                self.IRCBot = None

                        self.recordStats()
                    else:
                        print self.stream + " timing out: " + str(self.timeout)
                        self.timeout += 1
                elif self.IRCBot is None and self.config["ALWAYS_ONLINE"] is True:
                    #we need to start up IRC Bot even if stream is offline
                    self.IRCBot = TwitchIRCBot(self.stream, self.JSONfp, self.LOGfp, self.config)
                    if self.config["IRC_BOT"] is True:
                        self.IRCBot.setDaemon(False)
                        self.IRCBot.start()

            time.sleep(self.config["PARENT_THREAD_SLEEP_TIME"])

def main():
    sys.setdefaultencoding('utf-8')
    #set all streams to inactive, pull the streamers we want to track from the config
    inactiveStreams = config.STREAMERS[:]
    activeStreams = []
    while 1:
        for stream in inactiveStreams[:]:
            s = Stream(stream)
            s.setDaemon(False)
            #start the stream thread (calls Stream.run())
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