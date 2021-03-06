import datetime
import logging
import os
import requests
import config

"""
    Static "class" for twitch REST commands
"""

date = datetime.datetime.utcnow()
directory = './logs/' + date.strftime(config.LOG_FILE_FORMAT)
if not os.path.exists(os.path.dirname(directory)):
    os.makedirs(os.path.dirname(directory))
logging.basicConfig(filename=directory,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.DEBUG)

def getTwitchEmotes(stream):
    #format out request
    EMOTE_REQUEST ="https://api.twitch.tv/kraken/chat/" + stream + "/emoticons"
    twitchEmotes = []
    try:
        emoteResponse = requests.get(EMOTE_REQUEST)
    except requests.exceptions.ConnectionError:
        print "request failure: " + EMOTE_REQUEST
        logging.debug("twitch emotes request failure: " + EMOTE_REQUEST)
        #couldn't grab emotes, return empty list
        return []
    emoteObj = None
    try:
        #format response to json
        emoteObj = emoteResponse.json()
        allEmotes = emoteObj['emoticons']
        for emote in allEmotes:
            #dont count any emotes that are subscriber only
            if emote['subscriber_only'] is False:
                twitchEmotes.append(emote['regex'])

    except (TypeError, ValueError, KeyError):
        print "Error occurred getting stream information on " + stream \
              + " /// streamObj: " + emoteObj
        print emoteResponse
        logging.debug("Error occurred getting stream information on " + stream
                      + " /// streamObj: " + emoteObj)
        logging.debug(emoteResponse)
        #return empty list to indicate nothing was grabbed
        return []
    return twitchEmotes[:]

def getSubEmotes(stream):
    EMOTE_REQUEST ="https://api.twitch.tv/kraken/chat/" + stream + "/emoticons"
    subEmotes = []
    try:
        emoteResponse = requests.get(EMOTE_REQUEST)
    except requests.exceptions.ConnectionError:
        print "request failure: " + EMOTE_REQUEST
        logging.debug("sub emotes request failure: " + EMOTE_REQUEST)
        #couldn't grab emotes, return empty list
        return []
    emoteObj = None
    try:
        emoteObj = emoteResponse.json()
        allEmotes = emoteObj['emoticons']
        for emote in allEmotes:
            if emote['subscriber_only'] is True:
                subEmotes.append(emote['regex'])

    except (TypeError, ValueError, KeyError):
        print "Error occurred getting stream information on " + stream \
              + " /// streamObj: " + emoteObj
        print emoteResponse
        logging.debug("Error occurred getting stream information on " + stream
                      + " /// streamObj: " + emoteObj)
        logging.debug(emoteResponse)
        return []
    return subEmotes[:]

def getStreamInfo(stream):
    #API only shows the first 25 followed streams by default
    #defaults: offset = 0, limit = 25
    #https://github.com/justintv/Twitch-API/blob/master/v3_resources/follows.md#get-usersuserfollowschannels

    #request stream data
    STREAM_REQUEST = "https://api.twitch.tv/kraken/streams/" + stream
    streamResponse = None
    try:
       streamResponse = requests.get(STREAM_REQUEST)
    except requests.exceptions.ConnectionError:
        print "request failure: " + STREAM_REQUEST
        logging.debug(stream + " - stream info request failure: " + STREAM_REQUEST)
        return [None, None]

    #get stream info from streamResponse
    streamObj = None
    try:
        #we will continue to check for a valid streamObj until 5 minutes are up, that's our timeout
        streamObj = streamResponse.json()
        #stream object returned null, so stream is likely offline
        if streamObj['stream'] is None:
            #return nulls so that the thread will be exited
            #stream is offline, or we didn't receive anything from twitch
            return [config.DEAD_THREAD_IDENTIFIER, config.STR_STREAM_OFFLINE]
        viewerNum = streamObj['stream']['viewers']
        game = streamObj['stream']['game']
    except (TypeError, ValueError, KeyError):
        #Error occured, temp disconnect
        print "Error occurred getting stream information on " + stream
        print streamResponse
        logging.debug(stream + " - Error occurred getting stream information on " + stream)
        logging.debug(streamResponse)
        #something messed up, dont add anything to csv
        return [None, None]

    #return our relevant data
    return [viewerNum, game]

def isOnline(stream):
    #check if a stream is online by seeing if the object[stream] returns null
    STREAM_REQUEST = "https://api.twitch.tv/kraken/streams/" + stream
    streamResponse = None
    try:
       streamResponse = requests.get(STREAM_REQUEST)
    except requests.exceptions.ConnectionError:
        #print "request failure: " + STREAM_REQUEST
        logging.debug("isOnline request failure: " + STREAM_REQUEST)
        #get stream info from streamResponse
        return False
    try:
        streamObj = streamResponse.json()
        if streamObj['stream'] is None:
            return False
        #print stream + " is online!"
        #logging.info(stream + " is online!")
        return True
    except (TypeError, ValueError, KeyError):
        #Error occured, check to see if stream is offline or if temp disconnect
        print "Error occurred checking online status."
        print streamResponse
        logging.debug(stream + " - Error occurred checking online status.")
        logging.debug(streamResponse)
    return False