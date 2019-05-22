import time
import json
import requests

from datetime import datetime, timedelta
from multiprocessing.dummy import Pool
from elasticsearch import TransportError, ConnectionError, NotFoundError
from elasticsearch_dsl import Search

from project import app
from project.dns.dns import TagDetailsDoc

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

    
    try:
        latestDoc = getLatestDoc(indexName)
        timeStamp = datetime.strptime(latestDoc['time'], fmt)
        app.logger.debug(f"Search for latest doc returned {timeStamp}")
        return (now - timeStamp).total_seconds() / 60.0
    except Exception as e:
        raise Exception("Local DB may not exist: trying to find timestamp in {latestDoc} resulted in {e}")


def getTagInfo(tagName):
    '''
    Method that uses user supplied api key (.panrc) and gets back the info on
    the tag specified as tagName.  This doesn't take very long so we don't have
    to do all the crap we did when getting domain info
    Calls:
        calcCacheTimeout()

    '''
    searchURL = app.config["AUTOFOCUS_TAG_URL"] + f"{tagName}"
    headers = {"Content-Type": "application/json"}
    data = {"apiKey": app.config['AUTOFOCUS_API_KEY']}

    # Query AF and get the tag info to be stored in our local ES cache
    app.logger.debug(f'Gathering tag info for {tagName} (2 API-points)')
    queryResponse = requests.post(url=searchURL, headers=headers,
                                  data=json.dumps(data))
    queryData = queryResponse.json()

    app.logger.debug(f"getTagInfo() returns: {queryData}")

    return queryData


def processTag(tagName):
    '''
    Method determines if we have a local tag info cache or we need to go to AF
    and gather the info.  Returns the data for manipulation by the calling
    method
    '''
    tagDoc = False
    updateDetails = False
    afApiKey = app.config['AUTOFOCUS_API_KEY']
    retStatusFail = f'Failed to get info for {tagName} - FAIL'
    now = datetime.now().replace(microsecond=0).isoformat(' ')
    timeLimit = (datetime.now() - timedelta(days=app.config['DOMAIN_TAG_INFO_MAX_AGE']))
    tagGroupDict = [{"tag_group_name": "Undefined",
                     "description": "Tag has not been assigned to a group"}]

    app.logger.debug(f"Querying local cache for {tagName}")
    
    try:
        tagDoc = TagDetailsDoc.get(id=tagName)

        # check age of doc and set to update the details
        if timeLimit > tagDoc.doc_updated:
            app.logger.debug(f"Last updated can't be older than {timeLimit} " +
                             f"but it is {tagDoc.doc_updated} and we need to " +
                             f"update cache")
            updateDetails = True
            updateType = "Updating"
        else:
            # If the tag groups are empty send back Undefined
            if not tagDoc.tag_groups or tagDoc.tag_groups == "":
                app.logger.debug(f"No tag group found, setting to undefined")
                tagDoc.tag_groups = tagGroupDict
            # else:
            #     tagDoc.tag_groups = afTagData['tag_groups']

            app.logger.debug(f"Last updated can't be older than {timeLimit} " +
                             f"and {tagDoc.doc_updated} isn't, will not update cache")


    except NotFoundError as nfe:
        app.logger.info(f"No local cache found for tag {tagName} - Creating")
        updateDetails = True
        updateType = "Creating"
        time.sleep(5) 
        
        
    
    if updateDetails:
        afTagData = getTagInfo(tagName)
        # If we get the word 'message' in the return it means something went
        # wrong, so just return False
        if "message" not in afTagData:
            app.logger.debug(f"{updateType} doc for {tagName}")

            tagDoc = TagDetailsDoc(meta={'id': tagName}, name=tagName)
            tagDoc.tag = afTagData['tag']
            tagDoc.doc_updated = now
            tagDoc.type_of_doc = "tag-doc"
            tagDoc.processed = 1

            # If the tag groups are empty send back Undefined
            if not afTagData['tag_groups'] or afTagData['tag_groups'] == "":
                tagDoc.tag_groups = tagGroupDict
            else:
                tagDoc.tag_groups = afTagData['tag_groups']

            # Only set the doc_created attribute if we aren't updating
            if updateType == "Creating":
                tagDoc.doc_created = now

            app.logger.debug(f"tagDoc is {tagDoc.to_dict()} ")

            tagDoc.save()

            tagDoc = TagDetailsDoc.get(id=tagName)

        else:
            if "not found" in afTagData['message']:
                tagDoc = TagDetailsDoc(meta={'id': tagName}, name=tagName)
                print(f"{tagDoc} and {tagName}")
                tagDoc.tag = {"tag_name":tagName,"public_tag_name":tagName,
                              "tag_class":"Tag not found in AF",
                              "description":"Tag not found in AF"}
                tagDoc.tag_groups = tagGroupDict
                tagDoc.doc_updated = "2019-05-19T21:49:41"
                
                tagDoc.save()
    
    app.logger.debug(f"processTag() returns: " +
                     f"{tagDoc.tag['tag_name'],tagDoc.tag['public_tag_name']}" +
                     f"{tagDoc.tag['tag_class'],tagDoc.tag_groups[0]['tag_group_name']}," +
                     f"{tagDoc.tag['description']}")

    return (tagDoc.tag['tag_name'], tagDoc.tag['public_tag_name'],
            tagDoc.tag['tag_class'], tagDoc.tag_groups[0]['tag_group_name'],
            tagDoc.tag['description'])



def indexDump(indexName, sortField="@timestamp"):

    definedSearch = Search(index=indexName).sort({sortField: {"order" : "desc"}})
    return definedSearch.scan()


    