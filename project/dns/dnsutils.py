import datetime
import json
import time
from ast import literal_eval

import requests
from elasticsearch.exceptions import NotFoundError

from project import app
from project.dns.dns import AFDetailsDoc, TagDetailsDoc, DomainDetailsDoc


def updateAfStats():
    '''
    Update the sfn-details af-doc.
    If it doesn't exist, the 'upsert' does that for us.
    '''
    now = datetime.datetime.now()

    try:
        afDoc = AFDetailsDoc.get(id='af-details')

    except NotFoundError as nfe:
        app.logger.info(f"The af-details doc is not found - creating")

        afDoc = AFDetailsDoc(meta={'id': 'af-details'},
                             minute_points=0,
                             minute_points_remaining=0,
                             daily_points=0,
                             daily_points_remaining=0,
                             minute_bucket_start=now,
                             daily_bucket_start=now)
    # The AF Doc should exist by now

    # Just grab a tag that we know exists so we can get the rolling point total
    returnData = getTagInfo("WildFireTest")
    afInfo = returnData['bucket_info']

    try:
        app.logger.debug(f"Updating af-details with "
                         f"{afInfo['daily_points_remaining']} remaining points")
        # Update the af-details doc in the DB
        afDoc.minute_points = afInfo['minute_points']
        afDoc.minute_points_remaining = afInfo['minute_points_remaining']
        afDoc.daily_points = afInfo['daily_points']
        afDoc.daily_points_remaining = afInfo['daily_points_remaining']
        afDoc.minute_bucket_start = afInfo['minute_bucket_start']
        afDoc.daily_bucket_start = afInfo['daily_bucket_start']
        afDoc.save()
        app.logger.debug('MUEY BUENO')
    except Exception as ex:
        app.logger.error('NO BUENO')
        app.logger.error(ex)


def checkAfPoints(bucketInfo):
    '''
    Check to verify that the point totals for AF are not being sucked dry.  This
    function compares the current point total vs the configured lower limit
    using the AF_POINT_LOW and the AF_POINT_NOEXEC config parameters in the app
    or user limit set in .panrc file.  AF_POINT_LOW slows down execution of
    queries to AF, AF_POINT_NOEXEC stops execution for a period of time -
    AF_NOEXEC_CKTIME.
    '''

    pointsRemaining = bucketInfo['daily_points_remaining']
    noExecPoints = app.config['AF_POINT_NOEXEC']
    afPointLow = app.config['AF_POINTS_LOW']
    afNoExecTime = app.config['AF_NOEXEC_CKTIME']

    app.logger.debug(f"AF_POINTS SYSTEM settings: AF_POINT_NOEXEC: "
                     f"{noExecPoints}, AF_POINTS_LOW: {afPointLow}, "
                     f"AF_NOEXEC_CKTIME: {afNoExecTime}")

    # Check the points total against the AF_POINT_NOEXEC config parameter and
    # go into sleep mode for AF_NOEXEC_CKTIME to stop processing.
    if pointsRemaining <= noExecPoints:
        resetFlag = True
        while resetFlag:
            app.logger.info(f"Sleeping for {afNoExecTime} seconds because daily"
                            f" point total is {pointsRemaining}")
            time.sleep(afNoExecTime)
            newBucketInfo = getTagInfo("WildFireTest")
            if newBucketInfo['bucket_info']['daily_points_remaining'] > noExecPoints:
                resetFlag = False

    elif pointsRemaining < afPointLow:
        # Check the points against the configured low water mark.  If it's too
        # low set app config setting AF_POINTS_MODE to True - which will slow
        # down the processing to 1 event at a time.
        app.logger.info(f"Slowing down execution because daily "
                        f"point total is {pointsRemaining}")
        app.config['AF_POINTS_MODE'] = True
    else:
        # We probably hit a "minute points exceeded" so just wait for a minute
        # and then we continue execution
        time.sleep(60)
        # This resets it back to False if the AF points automatically reset
        app.logger.debug(f"Regular exec since daily point total is "
                         f" {pointsRemaining}")
        app.config['AF_POINTS_MODE'] = False


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
    app.logger.debug(f'Gathering tag info for {tagName}')
    queryResponse = requests.post(url=searchURL, headers=headers,
                                  data=json.dumps(data))
    queryData = queryResponse.json()

    app.logger.debug(f"getTagInfo() returns: {queryData}")

    return queryData


def processTagList(tagObj):
    tagList = list()
    sample = tagObj['_source']

    # If we have tags associated with samples, extract them for each
    # sample and then get their meta-data
    if 'tag' in sample:
        app.logger.debug(f"Found tag(s) {sample['tag']} in sample")

        for tagName in sample['tag']:
            app.logger.debug(f"Processing tag {tagName}")

            tagData = processTag(tagName)
            tagList.append(tagData)

            app.logger.debug(f"Tag data returned from processTag(): {tagData}")
    else:
        tagData = "NULL"

    app.logger.debug(f"processTagList() returns: {tagList}")

    return tagList


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
    now = datetime.datetime.now().replace(microsecond=0).isoformat(' ')
    timeLimit = (datetime.datetime.now() -
                 datetime.timedelta(days=app.config['DOMAIN_TAG_INFO_MAX_AGE']))
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
            app.logger.debug(f"Last updated can't be older than {timeLimit} " +
                             f"and {tagDoc.doc_updated} is not, so don't need" +
                             f" to update cache")


    except NotFoundError as nfe:
        app.logger.info(f"No local cache found for tag {tagName} - Creating")
        updateDetails = True
        updateType = "Creating"

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
            return False

    app.logger.debug(f"processTag() returns: " +
                     f"{tagDoc.tag['tag_name'],tagDoc.tag['public_tag_name']}" +
                     f"{tagDoc.tag['tag_class'],tagDoc.tag_groups[0]['tag_group_name']}," +
                     f"{tagDoc.tag['description']}")

    return (tagDoc.tag['tag_name'], tagDoc.tag['public_tag_name'],
            tagDoc.tag['tag_class'], tagDoc.tag_groups[0]['tag_group_name'],
            tagDoc.tag['description'])


def assessTags(tagsObj):
    '''
    Determine the most relevant tag based on samples and the dates associated
    with the tag.  Utilizes the CONFIDENCE_LEVELS dictionary set in the .panrc
    or the default values for confidence scoring
    '''
    confLevel = 5
    taggedEvent = False
    tagConfLevels = literal_eval(app.config['CONFIDENCE_LEVELS'])

    # Iterate over all tags until:
    #  Find a tag with campaign
    #    We're done and return
    #  Find an actor
    #    Set the tagInfo to this but keep going in case we find a campaign
    #  Find the *first* malware
    #    Set the tagInfo to this but keep going in case we find a campaign
    #      or an actor

    for entry in tagsObj:
        while not taggedEvent:
            sampleDate = entry[0]
            sampleFileType = entry[1]
            for tag in entry[2]:
                tagName = tag[1]
                tagClass = tag[2]
                tagGroup = tag[3]
                tagDesc = tag[4]

                app.logger.debug(f"Working on tag {tagName} " +
                                 f"with class of {tagClass}")

                # import pdb;pdb.set_trace()
                if tagClass == "campaign":
                    tagInfo = {"tag_name": tagName, "public_tag_name": tag[0],
                               "tag_class": tagClass, "sample_date": sampleDate,
                               "file_type": sampleFileType, "tag_group": tagGroup,
                               "description": tagDesc, "confidence_level": 90}
                    taggedEvent = True
                    app.logger.debug(f"Tag info for {tagName}: {tagInfo}")
                    break  # This the grand daddy of all tags
                    # No need to keep processing the rest

                elif tagClass == "actor":
                    tagInfo = {"tag_name": tagName, "public_tag_name": tag[0],
                               "tag_class": tagClass, "sample_date": sampleDate,
                               "file_type": sampleFileType, "tag_group": tagGroup,
                               "description": tagDesc, "confidence_level": 90}
                    taggedEvent = True
                    app.logger.debug(f"Tag info for {tagName}: {tagInfo}")


                elif (tagClass == "malware_family") and not taggedEvent:

                    # Figure out the confidence level for the malware based on how
                    # many days old it is.
                    dateDiff = (datetime.datetime.now() - datetime.datetime.strptime(sampleDate, "%Y-%m-%dT%H:%M:%S"))

                    app.logger.debug(f"Calculating confidence level: " +
                                     f"Day differential of {dateDiff.days}")

                    for days in tagConfLevels:
                        if dateDiff.days < int(days):
                            confLevel = tagConfLevels[days]
                            app.logger.debug(f"confidence_level for " +
                                             f"{tagName} @ date " +
                                             f"{sampleDate}: " +
                                             f"{confLevel} based on" +
                                             f" age of {dateDiff.days} days")
                            break  # We found the right confidence level
                        else:
                            confLevel = 5
                            app.logger.debug(f"confidence_level for " +
                                             f"{tagName} @ date " +
                                             f"{sampleDate}: " +
                                             f"{confLevel} based on" +
                                             f" age of {dateDiff.days} days")

                    tagInfo = {"tag_name": tagName, "public_tag_name": tag[0],
                               "tag_class": tagClass, "sample_date": sampleDate,
                               "file_type": sampleFileType, "tag_group": tagGroup,
                               "description": tagDesc, "confidence_level": confLevel}
                    taggedEvent = True
                    app.logger.debug(f"Tag info for {tagName}: {tagInfo}")

            # Went through all the tags available and none were of interest
            if not taggedEvent:
                tagInfo = {"tag_name": "Low Priority Tags",
                           "public_tag_name": "Low Priority Tags",
                           "tag_class": "Low Priority Tags",
                           "sample_date": "2000-01-01T00:00:00",
                           "file_type": "Low Priority Tags",
                           "tag_group": "Low Priority Tags",
                           "description": "Low Priority Tags",
                           "confidence_level": 0}
                taggedEvent = True

    app.logger.debug(f"assessTags() returns: {tagInfo}")

    return tagInfo


def getDomainInfo(threatDomain):
    '''
    Method that uses user supplied api key (.panrc) and gets back a "cookie."
    Loops through timer (in minutes) and checks both the timer value and the
    maximum search result percentage and returns the gathered domain data when
    either of those values are triggered
    '''
    domainObj = list()
    domainObj.append(('2000-01-01T00:00:00', 'NA',
                      [('No Samples Returned for Domain',
                        'No Samples Returned for Domain',
                        'No Samples Returned for Domain',
                        'No Samples Returned for Domain',
                        'No Samples Returned for Domain')]))
    apiKey = app.config['AUTOFOCUS_API_KEY']
    searchURL = app.config["AUTOFOCUS_SEARCH_URL"]
    resultURL = app.config["AUTOFOCUS_RESULTS_URL"]
    lookupTimeout = app.config["AF_LOOKUP_TIMEOUT"]
    maxPercentage = app.config["AF_LOOKUP_MAX_PERCENTAGE"]
    resultData = {"apiKey": apiKey}
    headers = {"Content-Type": "application/json"}
    searchData = {"apiKey": apiKey,
                  "query": {
                      "operator": "all",
                      "children": [{
                          "field": "alias.domain",
                          "operator": "contains",
                          "value": threatDomain}]},
                  "size": 100,
                  "from": 0,
                  "sort": {"create_date": {"order": "desc"}},
                  "scope": "global",
                  "artifactSource": "af"}

    # Query AF and it returns a "cookie" that we use to view the resutls of the
    # search

    app.logger.debug(f'Gathering domain info for {threatDomain}')
    queryResponse = requests.post(url=searchURL, headers=headers,
                                  data=json.dumps(searchData))
    app.logger.debug(f"Initial AF domain query returned {queryResponse.json()}")
    queryData = queryResponse.json()

    # If the response has a message in it, it most likely means we ran out of
    # AF points.
    if 'message' in queryData:
        if "Bucket Exceeded" in queryData['message']:
            app.logger.error(f"We have exceeded the daily allotment of points "
                             f"for AutoFocus - going into hibernation mode.")
            checkAfPoints(queryData['bucket_info'])
            # The checkAfPoints will eventually return after the points reset.
            # When they do, reurn the AF query so we don't lose it.
            app.logger.debug(f'Gathering domain info for {threatDomain}')
            queryResponse = requests.post(url=searchURL, headers=headers,
                                          data=json.dumps(searchData))
            app.logger.debug(f"Initial AF domain query returned "
                             f"{queryResponse.json()}")
            queryData = queryResponse.json()
        else:
            app.logger.error(f"Return from AutoFocus is in error: {queryData}")

    # Query should return an af_cookie or an error
    if 'af_cookie' in queryData:
        cookie = queryData['af_cookie']
        cookieURL = resultURL + cookie

        app.logger.debug(f"Cookie {cookie} returned for query of {threatDomain}")

        # Wait for the alloted time before querying AF for search results.  Do
        # check every minute anyway, in case the search completed as the cookie
        # is only valid for 2 minutes after it completes.
        for timer in range(lookupTimeout):
            time.sleep(61)
            cookieResults = requests.post(url=cookieURL, headers=headers,
                                          data=json.dumps(resultData))
            domainData = cookieResults.json()
            if domainData['af_complete_percentage'] >= maxPercentage:
                break
            else:
                app.logger.info(f"Search completion " +
                                f"{domainData['af_complete_percentage']}% for " +
                                f"{threatDomain} at {timer+1} minute(s): " +
                                f"{domainData}")

        if domainData['total'] != 0:
            for hits in domainData['hits']:
                tagList = processTagList(hits)
                # reset domainObj to empty then add the returned tagList
                domainObj = list()
                domainObj.append((hits['_source']['finish_date'],
                                  hits['_source']['filetype'],
                                  tagList))

        else:
            app.logger.info(f"No samples found for {threatDomain} in time "
                            f"allotted")


    else:
        app.logger.error(f"Unable to retrieve domain info from AutoFocus. "
                         f"The AF query returned {queryData}")

    app.logger.debug(f"getDomainInfo() returns: {domainObj}")

    return domainObj


def getDomainDoc(domainName):
    '''
    Method to get the local domain doc info and return it to the event
    processor so it can update the event with the most recent info
    '''
    domainDoc = "NULL"
    updateDetails = False
    now = datetime.datetime.now().replace(microsecond=0).isoformat(' ')
    timeLimit = (datetime.datetime.now() -
                 datetime.timedelta(days=app.config['DNS_DOMAIN_INFO_MAX_AGE']))

    app.logger.debug(f"Querying local cache for {domainName}")

    try:
        domainDoc = DomainDetailsDoc.get(id=domainName)

        # check age of doc and set to update the details
        if timeLimit > domainDoc.doc_updated:
            app.logger.debug(f"Domain last updated can't be older than "
                             f"{timeLimit} but the doc was last updated "
                             f" {domainDoc.doc_updated} so cache should be "
                             f"updated")
            updateDetails = True
            updateType = "Updating"
        else:
            app.logger.debug(f"Domain last updated can't be older than "
                             f"{timeLimit} and {domainDoc.doc_updated} is not, "
                             f"so don't need to update cache")

    except NotFoundError as nfe:
        app.logger.info(f"No local cache doc found for domain {domainName}")
        updateDetails = True
        updateType = "Creating"

    # Either we don't have it or we determined that it's too old
    if updateDetails:
        app.logger.info(f"{updateType} domain doc for domain {domainName}")
        try:
            afDomainData = getDomainInfo(domainName)
            domainDoc = DomainDetailsDoc(meta={'id': domainName}, name=domainName)
            domainDoc.tags = afDomainData
            domainDoc.doc_updated = now
            # Don't mess with the doc_created field if we are updating
            if "Creating" in updateType:
                domainDoc.doc_created = now

            domainDoc.save()

        except Exception as e:
            app.logger.error(f"Unable to work with domain doc {domainName} - {e}")
            domainDoc = "NULL"

    app.logger.debug(f"getDomainDoc() returns: {domainDoc}")

    return domainDoc
