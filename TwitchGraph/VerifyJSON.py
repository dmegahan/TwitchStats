import csv
import json
import re

__author__ = 'Danny'
"""This script will compare the number of emotes recorded in the json files with the messages recorded in the logs"""

def countJson(fp):
    with open(fp, 'r') as f:
        data = json.load(f)
        emotes = data['emotes']
    return emotes

def countLog(fp, emotes):
    with open(fp, 'rb') as csvfile:
            csvEmotes = {}
            for row in csvfile:
                for emote in emotes:
                    #line is constructed like time user: message
                    message = row.split(":")[-1]
                    message = message.rstrip()
                    if re.search(r'\b' + emote + r'\b', message):
                        #valid emote found, lets record it
                        if csvEmotes.has_key(emote):
                            old_val = csvEmotes[emote]
                            csvEmotes[emote] = (old_val + 1)
                        else:
                            csvEmotes[emote] = 1

    return csvEmotes

def compare():
    jsonEmotes = countJson("C:/Users/Danny/PycharmProjects/TwitchScrapper/TwitchGraph/data/trick2g/logs/D24_M04_Y2015_H00_m27_s36.json")
    emotes = []
    for key in jsonEmotes.keys():
        emotes.append(key)
    csvEmotes = countLog("C:/Users/Danny/PycharmProjects/TwitchScrapper/TwitchGraph/data/trick2g/logs/D24_M04_Y2015_H00_m27_s36.log", emotes)

    for key in set(csvEmotes.items()) & set(jsonEmotes.items()):
        print "jsonEmotes " + str(key[0]) + ": " + str(jsonEmotes[key[0]])
        print "csvEmotes " + str(key[0]) + ": " + str(csvEmotes[key[0]])

compare()