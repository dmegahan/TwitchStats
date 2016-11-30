# TwitchStats

__As of early 2016, this bot is no longer maintained. Some changes have occured with the Twitch API, and this bot does not reflect or implement those changes__

=======================

TwitchStats is a collection of python bots that tracks and records various statistics from Twitch.tv streams. 2 different bots are programmed to collect 2 different sets of data, one set of data from the stream statistics, and another set of data from the Twitch chat room. These statistics are logged and stored locally. This program can and does record statistics from multiple streams at one time.

The data specific data collected from the chat bot (TwitchIRCBot) includes emote usage and frequency, and it also collects and stores the complete chat logs from the stream session, as well as when the stream is offline. The emote data is stored as JSON, and the chat logs stored in .log files. 

Currently, the only stream statistics tracked are the viewer numbers and the game being played. These stats are stored as JSON as well, along with the time they were collected. The bot checks these statistics every few seconds, so a graph can be constructed. This graph is generated using [plot.ly](https://plot.ly/) automatically when the stream finishes. 

Along with capturing certain statistics, the program is set up in a modular way. The 2 bots operate independently, and either can be turned off or disabled without affecting anything else. Additionally, in the [config.py](https://github.com/dmegahan/TwitchStats/blob/master/TwitchGraph/config.py) file, configurations can be created for each different stream one wants to watch/track. 

Config settings include:
* where the data is stored
* how often data is collected
* which bots are active
* the special phrases that are tracked (not just emotes necessarily)
