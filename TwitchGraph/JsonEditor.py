import json
import os
import constants

__author__ = 'Danny'

class JsonEditor:
    def __init__(self, file, globalpath):
        #initialize the json file if empty
        self.directory = file
        self.globalJson = globalpath
        if not os.path.exists(os.path.dirname(self.directory)):
            os.makedirs(os.path.dirname(self.directory))
        self.initializeJson(file)
        #self.initializeStats(file)
        self.initializeGlobal(globalpath)

    def toJSON(self, stats):
        #takes in a dictionary of keys and values, to be put into the json file
        try:
            for key in stats:
                self.setValueForStat(key, stats[key])
        except TypeError:
            print "RECEIVED STATS: " + str(stats) + ", CAUSED ERROR in JSONEDITOR"

    def initializeJson(self, file):
        with open(file, 'w') as f:
            data = {}
            data['sub emotes'] = {}
            data['twitch emotes'] = {}
            data['stats'] = {}
            data['stats']['All'] = {}
            json.dump(data, f)
            f.seek(0)
            json.dump(data, f, indent=4)

    def initializeGlobal(self, file):
        if not os.path.isfile(file):
            with open(file, 'w') as f:
                data = {}
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

    def incrementSubEmote(self, emote):
        with open(self.directory, 'r+') as f:
            try:
                data = json.load(f)
            except ValueError:
                print self.directory + " encountered ValueError incrementing emote"
            try:
                old_val = data['sub emotes'][emote]
            except KeyError:
                old_val = 0
                data['sub emotes'][emote] = old_val
            #print "Incremented emote: " + emote + " to " + str((old_val+1))
            data['sub emotes'][emote] = (old_val + 1)
            f.seek(0)
            json.dump(data, f, indent=4)

    def incrementTwitchEmote(self, emote):
        with open(self.directory, 'r+') as f:
            data = json.load(f)
            try:
                old_val = data['twitch emotes'][emote]
            except KeyError:
                old_val = 0
                data['twitch emotes'][emote] = old_val
            #print "Incremented emote: " + emote + " to " + str((old_val+1))
            data['twitch emotes'][emote] = (old_val + 1)
            f.seek(0)
            json.dump(data, f, indent=4)

    def setValueForStat(self, stat, value):
        with open(self.directory, 'r+') as f:
            data = json.load(f)
            data['stats']['All'][stat] = value
            f.seek(0)
            json.dump(data, f, indent=4)

    def setValueForGlobalStat(self, stat, value):
        with open(self.globalJson, 'r+') as f:
            data = json.load(f)
            data['stats'][stat] = value
            f.seek(0)
            json.dump(data, f, indent=4)

