"""Controls the other classes, gives commands the user can use"""

from TwitchIRCBot import TwitchIRCBot
import TwitchBot.py

#not yet implemented
class Controller:
    def __init__(self):
        self.tGrab = TwitchBot()
        self.tIRCBot = TwitchIRCBot()

    def killThread(self, t):
        t.join()

    def status(self):
        self.tGrab.status
        self.tIRCBot.status

    def start(self):
        self.tGrab.main()
        self.tIRCBot.main()

def main():
    while 1:
        input = raw_input()

main()