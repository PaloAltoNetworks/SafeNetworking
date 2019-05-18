import time

from datetime import datetime
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
                .sort({"time.keyword": {"order" : "desc"}})
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

    now = datetime.utcnow()
    fmt = '%Y-%m-%d %H:%M:%S'

    latestDoc = getLatestDoc(indexName)
    try:
        timeStamp = datetime.strptime(latestDoc['time'], fmt)
        app.logger.debug(f"Search for latest doc returned {timeStamp}")
        print(f"{now}")
    except Exception as e:
        app.logger.error(f"Trying to find timestamp in {latestDoc} resulted in {e}")    

    return (now - timeStamp).total_seconds() / 60.0



def indexDump(indexName, sortField="@timestamp"):

    definedSearch = Search(index=indexName).sort({sortField: {"order" : "desc"}})
    return definedSearch[0:9999].execute()

    