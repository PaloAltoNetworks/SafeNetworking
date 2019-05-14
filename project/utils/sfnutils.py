import time
import datetime

from multiprocessing.dummy import Pool
from elasticsearch import TransportError, ConnectionError
from elasticsearch_dsl import Search

from project import app

def getLatestDoc(indexName):
    '''
    Get the last document indexed into inedexName
    '''
    # Create search for last doc
    try:
        eventSearch = Search(index=indexName) \
                .sort({"@timestamp": {"order" : "desc"}})
        eventSearch = eventSearch[:1]
        searchResponse = eventSearch.execute()
        app.logger.debug(f"getLatestDoc returns {searchResponse.hits[0]}")
        return searchResponse.hits[0]
    except Exception as e:
        app.logger.error(f"Search for latest doc in {indexName} resulted in error {e}")


def getLatestTime(indexName):
    '''
    Calculate the time delta between when the last doc was stored in the index
    indexName and now
    '''

    now = datetime.datetime.now()

    latestDoc = getLatestDoc(indexName)
    try:
        timeStamp = latestDoc['@timestamp']
        app.logger.debug(f"Search for latest doc returned {timeStamp}")
        return timeStamp
    except Exception as e:
        app.logger.error(f"Trying to find timestamp in {latestDoc} resulted in {e}")

    exit()
    
    # timeDiff = (now - searchResponse['@timestamp']
    #              datetime.timedelta(days=app.config['DOMAIN_TAG_INFO_MAX_AGE']))
    