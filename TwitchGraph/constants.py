#constants file

PARENT_THREAD_SLEEP_TIME = 60
TWITCH_THREAD_SLEEP_TIME = 0.75
IRC_THREAD_SLEEP_TIME = 1

#keep thread alive for 5 minutes before killing it for being offline
TIMEOUT = 5

DEAD_THREAD_IDENTIFIER = -1

STR_STREAM_OFFLINE = "Stream Offline!"

#STREAMERS = ["lirik", "itmejp", "summit1g", "destiny", "nl_kripp", "reckful", "sodapoppin",
          #   "dansgaming", "kaceytron", "watchmeblink1", "trick2g", "trumpsc"]

STREAMERS = ["lirik"]

LOGS_FOLDER = "./logs/"

TIME_FORMAT = "%H:%M:%S"
GRAPH_FILE_FORMAT = "D%d_M%m_Y%Y_H%H_m%M_s%S.csv"
JSON_FILE_FORMAT  = "D%d_M%m_Y%Y_H%H_m%M_s%S.json"
CHAT_LOG_FILE_FORMAT  = "D%d_M%m_Y%Y_H%H_m%M_s%S.log"

JSON_ATTRIBUTES = ["Peak Viewers", "Start Time", "End Time", "Average Viewers", "Time Streamed"]