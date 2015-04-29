import csv
import json
import os
import datetime
import logging
import plotly.plotly as py
from plotly.graph_objs import *
import time
import constants


class Graph:

    def __init__(self):
        date = datetime.datetime.utcnow().strftime("%d_%m_%Y")
        directory = constants.LOGS_FOLDER + date + ".log"
        if not os.path.exists(os.path.dirname(directory)):
            os.makedirs(os.path.dirname(directory))
        logging.basicConfig(filename=directory,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %H:%M:%S',
                            level=logging.DEBUG)

    """Creates a line graph from a CSV populated with viewer data from a stream"""
    def createGraphFromCSV(self, csvPath):
        splitPath = csvPath.split('/')[2:]
        streamer = splitPath[0]
        raw_date = splitPath[1].split('.',1)[0]
        date = splitPath[1].split('.',1)[0].replace('_','/')
        with open(csvPath, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            x_points = []
            y_points = []
            last_viewer_count = -1
            current_game_played = "Stream Started!"
            #games_graph is a list of scatter plots, each scatter plot being the views for a
            #different game
            games_graph = []
            for row in reader:
                #add row as a data point to graph
                #check for change in game
                if row[1] != current_game_played:
                    games_graph.append(Scatter(x=x_points, y=y_points,
                                               mode='lines',
                                               name=current_game_played))
                    current_game_played = row[1]
                    #clear the points lists, because we need to seperate the view nums for
                    #different games
                    #add the last point from last Scatter graph to new set of points, so that the graph is connected
                    last_x = x_points[-1:]
                    last_y = y_points[-1:]
                    x_points = [last_x]
                    y_points = [last_y]

                #need to check if viewer number is same as last point added
                #API doesnt constantly update viewer num,
                if row[0] != last_viewer_count:
                    last_viewer_count = row[0]
                    x_points.append(row[2])
                    y_points.append(row[0])

            title = streamer + "/" + raw_date
            layout = Layout(title=title,xaxis=XAxis(title='Time'),
                            yaxis=YAxis(title='Viewers'),
                            showlegend=True)

            data = Data(games_graph[1:])
            fig = Figure(data=data,layout=layout)
            print title + "created!"
            logging.info(title + " viewer graph created!")
            plot_url = py.plot(fig,filename=title, auto_open=False)

    def createGraphFromJson(self, jsonPath):
        splitPath = jsonPath.split('/')[2:]
        streamer = splitPath[0]
        raw_date = splitPath[1].split('.',1)[0]
        date = splitPath[1].split('.',1)[0].replace('_','/')
        with open(jsonPath) as f:
            data = json.load(f)
            emotes = data['emotes']
            x = []
            y = []
            for key, value in emotes.iteritems():
                x.append(key)
                y.append(value)
            data = ([Bar(x=x, y=y)])
            title = streamer + "/J" + raw_date
            logging.info(title + " emote graph created!")
            plot_url = py.plot(data, filename=title, auto_open=False)

#Graph().createGraphFromJson("C:/Users/Danny/PycharmProjects/TwitchScrapper/TwitchGraph/data/summit1g/logs/D24_M04_Y2015_H03_m47_s35.json")
