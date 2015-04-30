"""Controls the other classes, gives commands the user can use"""

from TwitchIRCBot import TwitchIRCBot
import TwitchGrab.py

class Controller:
    def __init__(self):
        self.tGrab = TwitchGrab()
        self.tIRCBot = TwitchIRCBot()

    def killThread(self, t):
        t.join()

    def status(self):
        self.tGrab.status
        self.tIRCBot.status

    def start(self):
        self.tGrab.main()
        self.tIRCBot.main()

    def end(self):


def main():
    while 1:
        input = raw_input()

main()