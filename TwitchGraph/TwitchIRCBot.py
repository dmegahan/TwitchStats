#IRC Bot to scrub Twitch chats for emotes
import logging
import os
import socket
import threading
import datetime
import time
import re
import requests
from JsonEditor import JsonEditor
from TwitchGraph import Graph
import constants
import json

logging.getLogger("requests").setLevel(logging.WARNING)

class ParentThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        #keeps track of streams that are offline, and checks on them periodically
        self.inactiveBots = constants.STREAMERS[:]
        self.threadsAlive = []

    def status(self):
        print "Active irc bots: " + str(self.threadsAlive)
        print "Inactive irc bots: " + str(self.inactiveBots)

    def isOnline(self, stream):
        #check if a stream is online by seeing if the object[stream] returns null
        STREAM_REQUEST = "https://api.twitch.tv/kraken/streams/" + stream
        streamResponse = None
        try:
           streamResponse = requests.get(STREAM_REQUEST)
        except requests.exceptions.ConnectionError:
            print "request failure: " + STREAM_REQUEST
            logging.debug("request failure: " + STREAM_REQUEST)
            #get stream info from streamResponse
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
            logging.debug("Error occurred checking online status.")
            logging.debug(streamResponse)

    def run(self):
        date = datetime.datetime.utcnow().strftime("%d_%m_%Y")
        directory = constants.LOGS_FOLDER + date + ".log"
        if not os.path.exists(os.path.dirname(directory)):
            os.makedirs(os.path.dirname(directory))
        logging.basicConfig(filename=directory,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %H:%M:%S',
                            level=logging.DEBUG)
        while 1:
            #start the threads up
            for stream in self.inactiveBots:
                #somehow to bot lost connection, try to reconnect
                if self.isOnline(stream):
                    t = TwitchIRCBot(stream)
                    t.setDaemon(False)
                    t.start()
                    #start a thread and add it to another list, threadsAlive
                    self.inactiveBots.remove(t.stream)
                    self.threadsAlive.append(t)

            #keep track of threads, if 1 ends, check up on it periodically
            for t in self.threadsAlive:
                #is the thread still alive?
                if not self.isOnline(t.stream):
                    #if stream is offline, dont log anything, kill the thread
                    #do some cleanup here if needed
                    if t.timeout > constants.TIMEOUT:
                        print t.stream + " is being killed."
                        t.toGraph()
                        t.join()
                    else:
                        print t.stream + " timing out: " + str(t.timeout)
                        t.timeout = t.timeout + 1

                if not t.isAlive():
                    #thread ended, put into dead thread list
                    self.inactiveBots.append(t.stream)
                    print t.stream + " bot died"
                    logging.info(t.stream + " bot died")
                    self.threadsAlive.remove(t)

            time.sleep(constants.PARENT_THREAD_SLEEP_TIME)

class TwitchIRCBot(threading.Thread):
    def __init__(self, stream, jsonName, logName):
        threading.Thread.__init__(self)

        self.user = "Kinetick42"
        self.token = "oauth:4eekng63twhsyg9fhlgtnu2ttghf4s"
        self.stream = stream
        self.chan = "#" + stream
        #incremented int value that keeps the thread alive till it reaches a certain number, ParentThread uses it
        self.timeout = 0
        self._stopevent = threading.Event( )
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.directory = './data/' + stream + '/logs/' + logName

        if not os.path.exists(os.path.dirname(self.directory)):
            os.makedirs(os.path.dirname(self.directory))

        self.jdirectory = './data/' + stream + '/logs/' + jsonName
        self.subEmotes = self.getEmotes()
        self.jEditor = JsonEditor(self.jdirectory, self.subEmotes)

    def getEmotes(self):
        EMOTE_REQUEST ="https://api.twitch.tv/kraken/chat/" + self.stream + "/emoticons"
        subEmotes = []
        try:
            emoteResponse = requests.get(EMOTE_REQUEST)
        except requests.exceptions.ConnectionError:
            print "request failure: " + EMOTE_REQUEST
            logging.debug("request failure: " + EMOTE_REQUEST)
            #couldn't grab emotes, return empty list
            return []
        emoteObj = None
        try:
            emoteObj = emoteResponse.json()
            allEmotes = emoteObj['emoticons']
            for emote in allEmotes:
                if emote['subscriber_only'] is True:
                    subEmotes.append(emote['regex'])

        except (TypeError, ValueError, KeyError):
            print "Error occurred getting stream information on " + self.stream \
                  + " /// streamObj: " + emoteObj
            print emoteResponse
            logging.debug("Error occurred getting stream information on " + self.stream
                          + " /// streamObj: " + emoteObj)
            logging.debug(emoteResponse)
            return []
        return subEmotes[:]

    def run(self):
        print "IRCBot " + self.stream + " started up!"
        logging.info("IRCBot " + self.stream + " started up!")
        self.connectToIRCChannel()

        #start constantly looking for recvs on the socket
        while not self._stopevent.isSet():
            self.readChat()
            self._stopevent.wait(constants.IRC_THREAD_SLEEP_TIME)

        print self.stream + " killed."

    def connectToIRCChannel(self):
        self.sock.connect(("irc.twitch.tv", 6667))
        print self.stream + " BOT connected to IRC server"
        logging.info(self.stream + " BOT connected to IRC server")
        #time.sleep(15)
        self.sock_send("PASS " + self.token + "\r\n")
        self.sock_send("NICK " + self.user + "\r\n")
        self.sock_send("JOIN " + self.chan + "\r\n")
        self.sock_recv()

    def readChat(self):
        lines = self.sock_recv()
        self.processLines(lines)

    def processLines(self, lines):
        #message received from Twitch has a lot of "filler" before the actual message, remove it
        #print lines
        #print self.stream + " ||||||||| " + str(lines)
        for line in lines:
            if "PRIVMSG" in line:
                #print self.stream + "||||||||||" + str(line)
                #twitch message starts with :, so chop it off
                #username is ended by !, so read until you get there
                message = ""
                try:
                    user = line.partition("!")[0][1:]
                    #print message
                    message = line.split(":")[2]
                    threading.Thread(target=self.processMessage(message))
                    self.toLog(user, message)
                except IndexError:
                    print "Error on line: " + message + " from " + user
                    logging.warning("Error on line: " + line + " message " + message + " from " + user)
            elif "PING" in line:
                #print "PING RECEIVED"
                self.sock_send("PONG :tmi.twitch.tv\r\n")

    def processMessage(self, message):
        for emote in self.subEmotes:
            try:
                message = message.rstrip()
                if re.search(r'\b' + emote + r'\b', message):
                    #valid emote found, lets record it

                    self.jEditor.incrementEmote(emote)
            except UnicodeDecodeError:
                print "UnicodeDecodeError on " + message
                logging.debug("UnicodeDecodeError on " + message)
                break;

    def sock_recv(self):
        try:
            recieve = self.sock.recv(4048)
        except socket.error as e:
            print self.stream + " received socket error: " + e
            logging.debug(self.stream + " received socket error: " + e)
        #print "received " + recieve
        lines = recieve.split("\r\n")[:-1] #last element will always be blank
        return lines

    def sock_send(self, message):
        try:
            self.sock.send(message)
        except socket.error as e:
            print self.stream + " received socket error: " + e
            logging.debug(self.stream + " received socket error: " + e)

    def toLog(self, user, message):
        exact_time = datetime.datetime.utcnow().strftime(constants.TIME_FORMAT)

        logThis = exact_time + " " + user + ": " + message
        with open(self.directory, 'a') as fp:
            #print self.stream + "|||||| " + message + " to " + str(self.directory)
            fp.write(logThis + "\r\n")

    def join(self, timeout=None):
        """ Stop the thread and wait for it to end. """
        self._stopevent.set( )
        threading.Thread.join(self, timeout)

"""
def main():
    botParent = ParentThread()
    botParent.setDaemon(False)
    botParent.start()
"""