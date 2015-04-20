import csv
import plotly.plotly as py
from plotly.graph_objs import *
import time

class Graph:
    def __init__(self, csvPath):
        splitPath = csvPath.split('/')[2:]
        self.streamer = splitPath[0]
        self.raw_date = splitPath[1].split('.',1)[0]
        self.date = splitPath[1].split('.',1)[0].replace('_','/')
        self.csvPath = csvPath
        self.createGraphFromCSV()

    def createGraphFromCSV(self):
        with open(self.csvPath, 'rb') as csvfile:
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

            title = self.streamer + "/" + self.raw_date
            layout = Layout(title=title)

            data = Data(games_graph[1:])
            fig = Figure(data=data,layout=layout)
            print title + "created!"
            plot_url = py.plot(fig,filename=title, auto_open=False)