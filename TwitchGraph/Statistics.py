import csv
import json
import logging
import os
import time
import datetime
import re
import TwitchAPI
import config
import constants
from JsonEditor import JsonEditor

__author__ = 'Danny'

class Statistics:
    def __init__(self, streamer, csvPath, jsonPath, logPath, globalPath, config):
        self.stream = streamer
        self.jsonPath = jsonPath
        self.csvPath= csvPath
        self.logPath = logPath
        self.globalPath = globalPath
        self.config = config
        self.jEditor = JsonEditor(self.jsonPath, self.globalPath)

        date = datetime.datetime.utcnow().strftime("%d_%m_%Y")
        directory = self.config["LOGS_FOLDER"] + date + ".log"
        if not os.path.exists(os.path.dirname(directory)):
            os.makedirs(os.path.dirname(directory))
        logging.basicConfig(filename=directory,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %H:%M:%S',
                            level=logging.DEBUG)

    def tallyEmotes(self):
        subEmotes = TwitchAPI.getSubEmotes(self.stream)
        twitchEmotes = TwitchAPI.getTwitchEmotes(self.stream)
        allEmotes = subEmotes + twitchEmotes

        with open(self.logPath, 'rb') as chatLog:
            for line in chatLog:
                split_line = line.split("]", 1)#index 0 will be the date and 1 will be everything else
                date = split_line[0].strip("[")
                user = split_line[1].split(":", 1)[0].strip()
                message = split_line[1].split(":", 1)[1]
                for emote in allEmotes:
                    try:
                        message = message.rstrip()
                        if re.search(r'\b' + emote + r'\b', message):
                            #valid emote found, lets record it
                            if emote in subEmotes:
                                self.jEditor.incrementSubEmote(emote)
                            elif emote in twitchEmotes:
                                self.jEditor.incrementTwitchEmote(emote)
                    except UnicodeDecodeError:
                        print "UnicodeDecodeError on " + message
                        logging.debug("UnicodeDecodeError on " + message)
                        break;

    def doDaily(self):
        #return a dict of json keys and values, to be added at the end of the stream
        jsonDict = {}
        a = self.getPeakViewers()
        jsonDict[a[0]] = a[1]
        self.updatePeakAllTimeViewers(a[0], a[1])
        a = self.getAverageViewers()
        jsonDict[a[0]] = a[1]
        self.updatePeakAverageViewers(a[0], a[1])
        #session is a nested list, and since we're looking for the total session we only expect 1 element returned
        stream_ses = self.getSessions()[0]
        jsonDict['Start Time'] = stream_ses[0]
        jsonDict['End Time'] = stream_ses[1]
        a = self.getTimeStreamed(stream_ses)
        jsonDict[a[0]] = a[1]
        self.updateTotalStreamTime(a[0], a[1])

        #game stats return a large dict of dicts (dict of games played, which each game having a dict of stats)
        a = self.getGameStatistics()
        jsonDict.update(a)

        return jsonDict

    def updateTotalStreamTime(self, key, stream_time):
        with open(self.globalPath, 'r+') as globalStats:
            data = json.load(globalStats)
            try:
                old_time = datetime.datetime.strptime(data['stats'][key], self.config['TIME_FORMAT'])
            except KeyError:
                data['stats'][key] = stream_time
                globalStats.seek(0)
                json.dump(data, globalStats, indent=4)
                return
            #print "Incremented emote: " + emote + " to " + str((old_val+1))
            stream_time = datetime.datetime.strptime(stream_time, self.config['TIME_FORMAT'])
            old_delta = datetime.timedelta(minutes=old_time.minute, seconds=old_time.second, hours=old_time.hour)
            stream_delta = datetime.timedelta(minutes=stream_time.minute,
                                              seconds=stream_time.second,
                                              hours=stream_time.hour)
            data['stats'][key] = str(old_delta + stream_delta)
            globalStats.seek(0)
            json.dump(data, globalStats, indent=4)

    def updatePeakAllTimeViewers(self, key, peak_viewers):
        with open(self.globalPath, 'r+') as globalStats:
            data = json.load(globalStats)
            try:
                old_val = data['stats'][key]
            except KeyError:
                old_val = 0
            #print "Incremented emote: " + emote + " to " + str((old_val+1))
            if old_val < peak_viewers:
                data['stats'][key] = peak_viewers
            globalStats.seek(0)
            json.dump(data, globalStats, indent=4)

    def updatePeakAverageViewers(self, key, average_viewers):
        with open(self.globalPath, 'r+') as globalStats:
            data = json.load(globalStats)
            try:
                old_val = data['stats'][key]
            except KeyError:
                old_val = 0
            #print "Incremented emote: " + emote + " to " + str((old_val+1))
            data['stats'][key] = (average_viewers + old_val / 2)
            globalStats.seek(0)
            json.dump(data, globalStats, indent=4)

    '''Daily stats'''
    def getGameStatistics(self):
        with open(self.csvPath, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            games = {}
            last_game = reader.next()[1]
            #reader.seek(0)
            games[last_game] = {}
            games[last_game]["sessions"] = {}
            for row in reader:
                if last_game != row[1]:
                    if row[1] != config.STR_STREAM_OFFLINE:
                        #new game, add to dict
                        last_game = row[1]
                        games[last_game] = {}
                        games[last_game]["sessions"] = {}

            #we got all the games, now lets find out their individual stats
            for game in games:
                sessions = self.getSessions(game)
                i = 0
                for session in sessions:
                    avg_viewers = self.getAverageViewersPerSession(session)
                    peak_viewers = self.getPeakViewersPerSession(session)
                    time_streamed = self.getTimeStreamed(session)
                    start_time = session[0]
                    end_time = session[1]

                    session_dict = {}
                    session_dict["Peak Viewers"] = peak_viewers
                    session_dict["Start Time"] = start_time
                    session_dict["End Time"] = end_time
                    session_dict["Average Viewers"] = avg_viewers
                    session_dict["Time Streamed"] = time_streamed[1]

                    session_name = "session" + str(i)
                    games[game]["sessions"][session_name] = session_dict
                    i += 1

        return games

    def getAverageViewersPerSession(self, session):
        #session currently is [start_time, end_time]
        with open(self.csvPath, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            start_time = datetime.datetime.strptime(session[0], self.config["DATE_TIME_FORMAT"])
            end_time = datetime.datetime.strptime(session[1], self.config["DATE_TIME_FORMAT"])
            total_viewers = 0
            lines_read = 0
            for row in reader:
                current_time = datetime.datetime.strptime(row[2], self.config["DATE_TIME_FORMAT"])
                if current_time >= start_time and current_time <= end_time:
                    #we're looking at the session data
                    total_viewers += int(row[0])
                    lines_read += 1
            #done, lets compute
            try:
                average_viewers = total_viewers / lines_read
            except ZeroDivisionError:
                average_viewers = -1
            return average_viewers

    def getPeakViewersPerSession(self, session):
        #session currently is [start_time, end_time]
        with open(self.csvPath, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            start_time = datetime.datetime.strptime(session[0], self.config["DATE_TIME_FORMAT"])
            end_time = datetime.datetime.strptime(session[1], self.config["DATE_TIME_FORMAT"])
            current_peak = -1
            for row in reader:
                current_time = datetime.datetime.strptime(row[2], self.config["DATE_TIME_FORMAT"])
                if current_time >= start_time and current_time <= end_time:
                    #we're looking at the session data
                    if int(current_peak) < int(row[0]):
                        current_peak = int(row[0])

            return current_peak

    def getPeakViewers(self, game=None):
        key = "Peak Viewers"
        with open(self.csvPath, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            peak = 0
            for row in reader:
                if game is not None:
                    #we're looking for a specific game here
                    if row[1] == game:
                        viewers = row[0]
                        if viewers > peak:
                            peak = viewers
                else:
                    viewers = row[0]
                    if int(viewers) > int(peak):
                        peak = viewers
        return key, peak

    def getAverageViewers(self, game=None):
        key = "Average Viewers"
        with open(self.csvPath, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            total_viewers = 0
            lines_read = 0
            for row in reader:
                if game is not None:
                    if row[1] == game:
                        total_viewers = total_viewers + int(row[0])
                        lines_read += 1
                else:
                    total_viewers = total_viewers + int(row[0])
                    lines_read += 1
            average_viewers = total_viewers/lines_read
        return key, average_viewers

    def getSessions(self, game=None):
        #this will get a list of sessions (each session has a start and end time). If a game is played mulitple
        #times in a stream, multiple sesions will be returned
        with open(self.csvPath, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            if game is not None:
                current_game = ""
                start_time = 0
                end_time = 0
                sessions = []
                session = []
                #retained to get accurate end time, since we wont know when a game ended until we reach a new game
                last_line = "";
                for row in reader:
                    if row[1] == game:
                        if current_game != game:
                            #first line of game found
                            start_time = row[2]
                            current_game = game
                    else:
                        if current_game == game:
                            #game session ended, wrap it up
                            end_time = last_line[2]
                            current_game = row[1]
                    last_line = row
                if end_time == 0:
                    #file ended, get last line
                    end_time = row[2]
                session.append(start_time)
                session.append(end_time)
                sessions.append(session)
                return sessions
            else:
                #get stream session
                first_line = reader.next()
                start_time = first_line[2]
                for row in reader:
                    pass
                stop_time = row[2]
                return [[start_time, stop_time]]

    def getStartTime(self, game=None):
        key = "Start Time"
        #read first line and set that as the start time
        with open(self.csvPath, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            first_line = reader.next()
            start_time = first_line[2]
        return key, start_time

    def getStopTime(self, game=None):
        key = "Stop Time"
        #read last line and set that as the stream end time
        with open(self.csvPath, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                pass
            stop_time = row[2]
        return key, stop_time

    def getTimeStreamed(self, session):
        key = "Time Streamed"
        start_time = session[0]
        stop_time = session[1]

        #convert times to a datetime object
        start = datetime.datetime.strptime(start_time, self.config["DATE_TIME_FORMAT"])
        end = datetime.datetime.strptime(stop_time, self.config["DATE_TIME_FORMAT"])

        diff = end - start
        days, seconds = diff.days, diff.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        return key, (str(hours) + ":" + str(minutes) + ":" + str(seconds))