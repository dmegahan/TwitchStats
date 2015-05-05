import csv
import os
import time
import datetime

__author__ = 'Danny'

class Statistics:
    def __init__(self, csvPath, jsonPath, logPath, globalPath):
        self.jsonPath = jsonPath
        self.csvPath= csvPath
        self.logPath = logPath
        self.globalPath = globalPath

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

    def getMostPlayedGame(self):
        print 1
    def getAverageTimeStreamed(self):
        print 1
    def mostPlayedGame(self):
        print 1
    def getMostPopularGame(self):
        print 1
    def getPeakAllTimeViewers(self):
        print 1

    '''Daily stats'''
    def getPeakViewers(self):
        key = "Peak Viewers"
        with open(self.csvPath, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            peak = 0
            for row in reader:
                viewers = row[0]
                if viewers > peak:
                    peak = viewers
        return key, peak

    def getAverageViewers(self):
        key = "Average Viewers"
        with open(self.csvPath, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            total_viewers = 0
            lines_read = 0
            for row in reader:
                total_viewers = total_viewers + int(row[0])
                lines_read += 1
            average_viewers = total_viewers/lines_read
        return key, average_viewers

    def getStartTime(self):
        key = "Start Time"
        #read first line and set that as the start time
        with open(self.csvPath, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            first_line = reader.next()
            start_time = first_line[2]
        return key, start_time

    def getStopTime(self):
        key = "Stop Time"
        #read last line and set that as the stream end time
        with open(self.csvPath, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                pass
            stop_time = row[2]
        return key, stop_time

    def getTimeStreamed(self):
        key = "Time Streamed"
        start_time = self.getStartTime()[1]
        stop_time = self.getStopTime()[1]

        #convert times to a datetime object
        start = datetime.datetime.strptime(start_time, "%H:%M:%S")
        end = datetime.datetime.strptime(stop_time, "%H:%M:%S")

        if end < start:
            #stream ran overnight, like 8pm - 2am, so we "make up" dates to easily compare the times
            start = datetime.datetime.strptime("1/1/2015 " + start_time, "%m/%d/%Y %H:%M:%S")
            end = datetime.datetime.strptime("1/2/2015 " + stop_time, "%m/%d/%Y %H:%M:%S")

        diff = end - start
        days, seconds = diff.days, diff.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        return key, (str(hours) + ":" + str(minutes) + ":" + str(seconds))

stats = Statistics("./data/summit1g/D02_M05_Y2015_H01_m02_s56.csv",
                   "./data/summit1g/logs/D02_M05_Y2015_H01_m02_s56.json",
                   "./data/summit1g/logs/D02_M05_Y2015_H01_m02_s56.log",
                   "./data/summit1g/logs/summit1g.json")
stats.doDaily()