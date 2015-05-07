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
        a = self.getStartTime()
        jsonDict[a[0]] = a[1]
        a = self.getStopTime()
        jsonDict[a[0]] = a[1]
        a = self.getTimeStreamed()
        jsonDict[a[0]] = a[1]

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

    '''Daily stats'''
    def getGameStatistics(self):
        with open(self.csvPath, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            games = {}
            last_game = reader.next()
            reader.seek(0)
            games[last_game] = {}
            for row in reader:
                if last_game != row[1]:
                    #new game, add to dict
                    last_game = row[1]
                    games[last_game] = {}

            #we got all the games, now lets find out their individual stats

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

    def getTimeStreamed(self, game=None):
        key = "Time Streamed"
        start_time = self.getStartTime()[1]
        stop_time = self.getStopTime()[1]

        #convert times to a datetime object
        start = datetime.datetime.strptime(start_time, self.config["TIME_FORMAT"])
        end = datetime.datetime.strptime(stop_time, self.config["TIME_FORMAT"])

        diff = end - start
        days, seconds = diff.days, diff.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        return key, (str(hours) + ":" + str(minutes) + ":" + str(seconds))

"""
stats = Statistics("./data/summit1g/D02_M05_Y2015_H01_m02_s56.csv",
                   "./data/summit1g/logs/D02_M05_Y2015_H01_m02_s56.json",
                   "./data/summit1g/logs/D02_M05_Y2015_H01_m02_s56.log",
                   "./data/summit1g/logs/summit1g.json")
stats.doDaily()
"""