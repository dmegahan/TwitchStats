#global constants
DEAD_THREAD_IDENTIFIER = -1
STR_STREAM_OFFLINE = "Stream Offline!"
#list of streamers to gather data from
STREAMERS = ["lirik", "itmejp", "summit1g", "destiny", "nl_kripp", "reckful", "sodapoppin",
             "dansgaming", "kaceytron", "watchmeblink1", "trick2g", "trumpsc", "kinetick42"]
JSON_ATTRIBUTES = ["Peak Viewers", "Start Time", "End Time", "Average Viewers", "Time Streamed"]

LOG_FILE_FORMAT = "%d_%m_%Y",

#config users is a dictionary of lists, each key in the dictionary being a matching config key
#if you want to have another stream use a different configuration, add the configuration key to the dictionary, and
#add the streamer name, to the corresponding list
#input must match the streamer name and config file you want to use
#Example: "new_config": ["sodapoppin", "lirik", "summit1g"]

config_users = {
    "destiny_config": ["destiny"]
}

config = {
    "default": {
        "PARENT_THREAD_SLEEP_TIME": 60,
        "TWITCH_THREAD_SLEEP_TIME": 0.75,
        "IRC_THREAD_SLEEP_TIME": 1,
        "TIMEOUT": 5,
        "MATCH_PHRASES": ["BabyRage NEVER LUCKY BabyRage",],
        "LOGS_FOLDER": "/logs/",
        "STATS_FOLDER": "/stats/",
        "CSV_FOLDER": "/CSV/",
        "DATE_TIME_FORMAT": "%B %d %Y %H:%M:%S",
        "LOG_TIME_FORMAT": "%B %d %Y %H:%M:%S %Z",
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
    },
    "destiny_config": {
        "PARENT_THREAD_SLEEP_TIME": 60,
        "TWITCH_THREAD_SLEEP_TIME": 0.75,
        "IRC_THREAD_SLEEP_TIME": 1,
        "TIMEOUT": 5,
        "MATCH_PHRASES": ["DANKMEMES",],
        "LOGS_FOLDER": "/logs/",
        "STATS_FOLDER": "/stats/",
        "CSV_FOLDER": "/CSV/",
        "DATE_TIME_FORMAT": "%B %d %Y %H:%M:%S",
        "LOG_TIME_FORMAT": "%B %d %Y %H:%M:%S %Z",
        "TIME_FORMAT": "%H:%M:%S",
        "GRAPH_FILE_FORMAT": "D%d_M%m_Y%Y_H%H_m%M_s%S.csv",
        "JSON_FILE_FORMAT": "D%d_M%m_Y%Y_H%H_m%M_s%S.json",
        "CHAT_LOG_FILE_FORMAT": "D%d_M%m_Y%Y_H%H_m%M_s%S.log",
        "RECONNECT_TIME": 360,

        #enable bot that reads stream IRC?
        "IRC_BOT": False,
        #enable bot that grabs stream data using Twitch API?
        "TWITCH_BOT": True,
        "ALWAYS_ONLINE": False,
    }
}