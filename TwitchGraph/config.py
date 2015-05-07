#global constants
DEAD_THREAD_IDENTIFIER = -1
STR_STREAM_OFFLINE = "Stream Offline!"
#list of streamers to gather data from
STREAMERS = ["lirik", "itmejp", "summit1g", "destiny", "nl_kripp", "reckful", "sodapoppin",
             "dansgaming", "kaceytron", "watchmeblink1", "trick2g", "trumpsc", "kinetick42"]
JSON_ATTRIBUTES = ["Peak Viewers", "Start Time", "End Time", "Average Viewers", "Time Streamed"]

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
        "TIME_FORMAT": "%B %d %Y %H:%M:%S",
        "CSV_TIME_FORMAT": "%H:%M:%S",
        "GRAPH_FILE_FORMAT": "D%d_M%m_Y%Y_H%H_m%M_s%S.csv",
        "JSON_FILE_FORMAT": "D%d_M%m_Y%Y_H%H_m%M_s%S.json",
        "CHAT_LOG_FILE_FORMAT": "D%d_M%m_Y%Y_H%H_m%M_s%S.log",
        "LOG_FILE_FORMAT": "%d_%m_%Y",
        "RECONNECT_TIME": 360,
    }
}