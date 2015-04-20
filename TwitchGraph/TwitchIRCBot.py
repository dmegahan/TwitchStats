#IRC Bot to scrub Twitch chats for emotes
import os
import socket
import threading
import datetime
import time
import constants

class ParentThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        #keeps track of streams that are offline, and checks on them periodically
        self.inactiveBots = constants.STREAMERS[:]
        self.threadsAlive = []

    def run(self):
        while 1:
            #start the threads up
            for stream in self.inactiveBots:
                #somehow to bot lost connection, try to reconnect
                t = TwitchIRCBot(stream)
                t.setDaemon(False)
                t.start()
                #start a thread and add it to another list, threadsAlive
                self.inactiveBots.remove(t.stream)
                self.threadsAlive.append(t)

            #keep track of threads, if 1 ends, check up on it periodically
            for t in self.threadsAlive:
                #is the thread still alive?
                if not t.isAlive():
                    #thread ended, put into dead thread list
                    self.inactiveBots.append(t.stream)
                    print t.stream + " bot died"
                    self.threadsAlive.remove(t)

            time.sleep(constants.PARENT_THREAD_SLEEP_TIME)

class TwitchIRCBot(threading.Thread):
    def __init__(self, stream):
        threading.Thread.__init__(self)

        self.user = "Kinetick42"
        self.token = "oauth:4eekng63twhsyg9fhlgtnu2ttghf4s"
        self.stream = stream
        self.chan = "#" + stream
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        date = datetime.datetime.utcnow().strftime("%d_%m_%Y")
        self.directory = './data/' + stream + '/logs/' + date + '.log'

    def run(self):
        print "IRCBot " + self.stream + " started up!"
        self.connectToIRCChannel()

        #start constantly looking for recvs on the socket
        self.readChat()

    def connectToIRCChannel(self):
        self.sock.connect(("irc.twitch.tv", 6667))
        #time.sleep(60)
        self.sock_send("PASS " + self.token + "\r\n")
        self.sock_send("NICK " + self.user + "\r\n")
        self.sock_send("JOIN " + self.chan + "\r\n")
        self.sock_recv()

    def readChat(self):
        while 1:
            lines = self.sock_recv()
            self.processLines(lines)


    def processLines(self, lines):
        #message received from Twitch has a lot of "filler" before the actual message, remove it
        for line in lines:
            if "PRIVMSG" in line:
                #twitch message starts with :, so chop it off
                #username is ended by !, so read until you get there
                try:
                    user = line.partition("!")[0][1:]
                    #print message
                    message = line.split(":")[2]
                except IndexError:
                    print "Error on line: " + message + " from " + user

                self.toLog(user, message)


    def sock_recv(self):
        recieve = self.sock.recv(4048)
        #print "received " + recieve
        lines = recieve.split("\r\n")
        return lines

    def sock_send(self, message):
        self.sock.send(message)

    def toLog(self, user, message):
        exact_time = datetime.datetime.utcnow().strftime("%H:%M:%S")

        if not os.path.exists(os.path.dirname(self.directory)):
            os.makedirs(os.path.dirname(self.directory))

        logThis = exact_time + " " + user + ": " + message
        with open(self.directory, 'a') as fp:
            fp.write(logThis + "\r\n")


def main():
    botParent = ParentThread()
    botParent.setDaemon(False)
    botParent.start()