import csv
import time

__author__ = 'Danny'

class Statistics:
    def __init__(self, jsonPath, csvPath):
        self.jsonPath = jsonPath
        self.csvPath = csvPath

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
        with open(self.csvFile, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            peak = 0
            for row in reader:
                viewers = row.split(",")[0]
                if viewers > peak:
                    peak = viewers
        return viewers

    def getAverageViewers(self):
        with open(self.csvFile, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            total_viewers = 0
            lines_read = 0
            for row in reader:
                total_viewers = total_viewers + row.split(",")[0]
                ++lines_read
            average_viewers = total_viewers/lines_read
        return average_viewers

    def getStartTime(self):
        #read first line and set that as the start time
        with open(self.csvFile, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            first_line = reader.next()
            start_time = first_line.split(",")[0]
        return start_time

    def getStopTime(self):
        #read last line and set that as the stream end time
        with open(self.csvFile, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                pass
            stop_time = row.split(",")[2]
        return stop_time

    def getTimeStreamed(self):
        start_time = self.getStartTime()
        stop_time = self.getStopTime()

        #convert times to a datetime object
        start = time.strptime(start_time, "%H:%M:%S")
        end = time.strptime(stop_time, "%H:%M:%S")

        if end < start:
            #stream ran overnight, like 8pm - 2am, so we "make up" dates to easily compare the times
            start = time.strptime("1/1/2015 " + start_time, "%m/%d/%Y %H:%M:%S")
            end = time.strptime("1/2/2015 " + stop_time, "%m/%d/%Y %H:%M:%S")

        diff = end - start
        days, seconds = diff.days, diff.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        return hours + ":" + minutes + ":" + seconds
