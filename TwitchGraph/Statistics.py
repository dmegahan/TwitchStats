import csv
import os
import time
import datetime
import constants

__author__ = 'Danny'

class Statistics:
    def __init__(self, csvPath, jsonPath, logPath, globalPath, config):
        self.jsonPath = jsonPath
        self.csvPath= csvPath
        self.logPath = logPath
        self.globalPath = globalPath
        self.config = config

    def doDaily(self):
        #return a dict of json keys and values, to be added at the end of the stream
        jsonDict = {}
        a = self.getPeakViewers()
        jsonDict[a[0]] = a[1]
        a = self.getAverageViewers()
        jsonDict[a[0]] = a[1]
        #session is a nested list, and since we're looking for the total session we only expect 1 element returned
        stream_ses = self.getSessions()[0]
        jsonDict['Start Time'] = stream_ses[0]
        jsonDict['End Time'] = stream_ses[1]
        #a = self.getTimeStreamed(stream_ses)
        #jsonDict[a[0]] = a[1]

        #game stats return a large dict of dicts (dict of games played, which each game having a dict of stats)
        a = self.getGameStatistics()
        jsonDict.update(a)

        return jsonDict

    def doAllTime(self):
        print 1

    def getMostPlayedGame(self):
        print 1

    def getAverageTimeStreamed(self):
        print 1

    def getMostPopularGame(self):
        print 1

    def getPeakAllTimeViewers(self):
        print 1

    def getTotalStreamHorus(self):
        print 1

    '''Daily stats'''
    def getGameStatistics(self):
        with open(self.csvPath, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            games = {}
            last_game = reader.next()[1]
            #reader.seek(0)
            games[last_game] = {}
            games[last_game]["sessions"] = []
            for row in reader:
                if last_game != row[1]:
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
                    session_dict["Time Streamed"] = time_streamed

                    games[game]["sessions"]["session" + str(i)] = session_dict
                    i += 1

        return games

    def getAverageViewersPerSession(self, session):
        #session currently is [start_time, end_time]
        with open(self.csvPath, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            start_time = datetime.datetime.strptime(session[0], self.config["DATE_TIME_FORMAT"])
            end_time = datetime.datetime.strptime(session[1], self.config["DATE_TIME_FORMAT"])
            for row in reader:
                current_time = datetime.datetime.strptime(row[2], self.config["DATE_TIME_FORMAT"])
                total_viewers = 0
                lines_read = 0
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
            for row in reader:
                current_time = datetime.datetime.strptime(row[2], self.config["DATE_TIME_FORMAT"])
                current_peak = -1
                if current_time >= start_time and current_time <= end_time:
                    #we're looking at the session data
                    if current_peak < row[0]:
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
                    if viewers > peak:
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
                for row in reader:
                    if row[1] == game:
                        if current_game != game:
                            #first line of game found
                            start_time = row[2]
                            current_game = game
                    else:
                        if current_game == game:
                            #game session ended, wrap it up
                            end_time = row[2]
                            current_game = row[1]
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
import JsonEditor

jsonFile = JsonEditor.JsonEditor("./data/summit1g/stats/D11_M05_Y2015_H17_m33_s56.json", "")
stats = Statistics("./data/summit1g/CSV/D11_M05_Y2015_H17_m33_s56.csv",
                   "./data/summit1g/stats/D11_M05_Y2015_H17_m33_s56.json",
                   "./data/summit1g/logs/D11_M05_Y2015_H17_m33_s56.log",
                   "./data/summit1g/logs/summit1g.json",
                   {
                        "PARENT_THREAD_SLEEP_TIME": 60,
                        "TWITCH_THREAD_SLEEP_TIME": 0.75,
                        "IRC_THREAD_SLEEP_TIME": 1,
                        "TIMEOUT": 5,
                        "MATCH_PHRASES": ["BabyRage NEVER LUCKY BabyRage",],
                        "LOGS_FOLDER": "/logs/",
                        "STATS_FOLDER": "/stats/",
                        "CSV_FOLDER": "/CSV/",
                        "DATE_TIME_FORMAT": "%B %d %Y %H:%M:%S",
                        "TIME_FORMAT": "%H:%M:%S",
                        "GRAPH_FILE_FORMAT": "D%d_M%m_Y%Y_H%H_m%M_s%S.csv",
                        "JSON_FILE_FORMAT": "D%d_M%m_Y%Y_H%H_m%M_s%S.json",
                        "CHAT_LOG_FILE_FORMAT": "D%d_M%m_Y%Y_H%H_m%M_s%S.log",
                        "LOG_FILE_FORMAT": "%d_%m_%Y",
                        "RECONNECT_TIME": 360,

                        #enable bot that reads stream IRC?
                        "IRC_BOT": True,
                        #if true, this will cause the IRC Bot to never stop reading chat, even if the streamer goes offline
                        "ALWAYS_ONLINE": False,
                        #enable bot that grabs stream data using Twitch API?
                        "TWITCH_BOT": True,
                    })
dailyStats = stats.doDaily()
jsonFile.toJSON(dailyStats)