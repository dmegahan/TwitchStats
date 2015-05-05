import json
import os
import constants

__author__ = 'Danny'

class JsonEditor:
    def __init__(self, file, emotesList):
        #initialize the json file if empty
        self.emotesList = emotesList
        self.directory = file
        if not os.path.exists(os.path.dirname(self.directory)):
            os.makedirs(os.path.dirname(self.directory))
        self.initializeJson(file)
        self.initializeStats(file)
        self.initializeEmotes(file)

    def toJSON(self, stats):
        #takes in a dictionary of keys and values, to be put into the json file
        for key in stats:
            self.setValueForStat(key, stats[key])

    def initializeJson(self, file):
        with open(file, 'w') as f:
            data = {}
            data['emotes'] = {}
            data['stats'] = {}
            json.dump(data, f)
            f.seek(0)
            json.dump(data, f, indent=4)

    def initializeStats(self, file):
        with open(file, 'r+') as f:
            data = json.load(f)
            for attr in constants.JSON_ATTRIBUTES:
                data['stats'][attr] = 0
            f.seek(0)
            json.dump(data, f, indent=4)

    def initializeEmotes(self, file):
        with open(file, 'r+') as f:
            data = json.load(f)
            for emote in self.emotesList:
                data['emotes'][emote] = 0
            f.seek(0)
            json.dump(data, f, indent=4)

    def incrementEmote(self, emote):
        with open(self.directory, 'r+') as f:
            data = json.load(f)
            old_val = data['emotes'][emote]
            #print "Incremented emote: " + emote + " to " + str((old_val+1))
            data['emotes'][emote] = (old_val + 1)
            f.seek(0)
            json.dump(data, f, indent=4)

    def setValueForStat(self, stat, value):
        with open(self.directory, 'r+') as f:
            data = json.load(f)
            data['stats'][stat] = value
            f.seek(0)
            json.dump(data, f, indent=4)