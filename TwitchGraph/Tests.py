from Statistics import Statistics
import JsonEditor
import unittest

class TestStatistics(unittest.TestCase):
    def setUp(self):
        self.config = {
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
                        "RECONNECT_TIME": 360,

                        #enable bot that reads stream IRC?
                        "IRC_BOT": True,
                        #if true, this will cause the IRC Bot to never stop reading chat, even if the streamer goes offline
                        "ALWAYS_ONLINE": False,
                        #enable bot that grabs stream data using Twitch API?
                        "TWITCH_BOT": True,
                    }

        self.jsonFile = JsonEditor.JsonEditor("./data/_TEST_/stats/D13_M05_Y2015_H20_m00_s45.json", "./data/_TEST_/logs/_TEST_.json")
        self.stats = Statistics("_TEST_", "./data/_TEST_/CSV/D13_M05_Y2015_H20_m00_s45.csv",
                                        "./data/_TEST_/stats/D13_M05_Y2015_H20_m00_s45.json",
                                        "./data/_TEST_/logs/D13_M05_Y2015_H20_m00_s45.log",
                                        "./data/_TEST_/logs/_TEST_.json", self.config)

    def test_tallyEmotes(self):
        #self.stats.tallyEmotes()
        print "Tally emotes done!"

    def test_doDaily(self):
        dailyStats = self.stats.doDaily()
        self.jsonFile.toJSON(dailyStats)

    def test_peakViewers(self):
        self.assertEqual(self.stats.getPeakViewers()[1], 3576)

    def test_averageViewers(self):
        print "AV: " + str(self.stats.getAverageViewers())

    def test_timeStreamed(self):
        stream_ses = self.stats.getSessions()[0]
        self.assertEqual(self.stats.getTimeStreamed(stream_ses)[1], "7:18:45")