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

class TwitchIRCBot(threading.Thread):
    def __init__(self, stream, jsonPath, logPath):
        threading.Thread.__init__(self)

        self.user = "Kinetick42"
        self.token = "oauth:4eekng63twhsyg9fhlgtnu2ttghf4s"
        self.stream = stream
        self.chan = "#" + stream
        #incremented int value that keeps the thread alive till it reaches a certain number, ParentThread uses it
        self.timeout = 0
        self._stopevent = threading.Event( )
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.directory = logPath

        if not os.path.exists(os.path.dirname(self.directory)):
            os.makedirs(os.path.dirname(self.directory))

        self.jdirectory = jsonPath
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