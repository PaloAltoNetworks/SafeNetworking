import time
import datetime
from project import app
from elasticsearch_dsl import Search
from multiprocessing.dummy import Pool
from project.dns.dns import DNSEventDoc
from elasticsearch import TransportError
from elasticsearch_dsl import connections
from project.dns.dnsutils import getDomainDoc, assessTags


def processDNS():
    '''
    This function is used to gather the unprocessed docs in ElasticSearch and
    put them into one of two lists - primary (named threats) or secondary
    ("generic") threats.  It will process the latest document up to the maximum
    defined number of documents (DNS_INIT_QUERY_SIZE).  The primary threats will
    be processed in real-time using multiprocessing.  The generic threats will be
    processed after the primary threats are done.
    '''
    now = datetime.datetime.now()
    priDocIds = list()
    secDocIds = list()
    qSize = app.config["DNS_EVENT_QUERY_SIZE"]
    
    app.logger.debug(f"Gathering {qSize} sfn-dns-events from ElasticSearch")

    # Define the default Elasticsearch client
    connections.create_connection(hosts=[app.config['ELASTICSEARCH_HOST']])

    # Create search for all unprocessed events
    eventSearch = Search(index="threat-*") \
                .query("match", tags="DNS") \
                .query("match", ** { "SFN.processed":0})  \
                .sort({"@timestamp": {"order" : "desc"}})

    # Limit the size of the returned docs to the specified config paramter and 
    # then exec the search
    eventSearch = eventSearch[:qSize]
    searchResponse = eventSearch.execute()

    print(searchResponse)

    # For each hit, classify the event as either primary (we have the domain
    # info cached) or secondary (need to look it up).
    # There will be a list for primary and secondary lookups.  Each list
    # has entries of dictionaires which contain the domain name, the index of
    # the event and the doc ID for that event.
    for hit in searchResponse.hits:
        entry = dict()
        domainName = hit['SFN']['domain_name']
        eventDoc = hit.meta.id
        eventIndex = hit.meta.index
        
        # Check to see if we have a domain doc for it already.  If we do,
        # add it to be processed first, if not, add it to the AF lookup
        # queue (secDocIds)
        domainSearch = Search(index="sfn-domain-details") \
                        .query("match", name=domainName)
        if domainSearch.execute():
            entry['document'] = eventDoc
            entry['index'] = eventIndex
            entry['domain_name'] = domainName
            priDocIds.append(entry)
            
        else:
            entry['document'] = eventDoc
            entry['index'] = eventIndex
            entry['domain_name'] = domainName
            secDocIds.append(entry)
            app.logger.debug(f"{eventDoc} : {entry}")

    app.logger.debug(f"priDocIds are {priDocIds}")
    app.logger.debug(f"secDocIds are {secDocIds}")

    # The lists are made, now continue to process each entry in the list(s)
    # If we aren't in DEBUG mode (.panrc setting)
    if not (app.config['DEBUG_MODE']) or (app.config['AF_POINTS_MODE']):

        # Set the number of multi processes to use and cap it at 16 so
	    # so we don't blow out the minute points on AutoFocus
        multiProcNum = app.config['DNS_POOL_COUNT'] if app.config['DNS_POOL_COUNT'] <= 16 else 16

        # Multiprocess the primary keys
        app.logger.debug(f"Running pri-keys through on {multiProcNum} processes")
        with Pool(multiProcNum) as pool:
            results = pool.map(searchDomain, priDocIds)

        app.logger.debug(f"Results for processing primary events {results}")

        # Do the same with the generic/secondary keys and pace so we don't kill AF
        app.logger.debug(f"Running sec-keys through on {multiProcNum} processes")
        with Pool(multiProcNum) as pool:
            results = pool.map(searchDomain, secDocIds)

        app.logger.debug(f"Results for processing AF lookup events {results}")

    # This else gets triggered so we only do one document at a time and is for
    # debugging at a pace that doesn't overload the logs. Load the secondary
    # docs as well, in case we run out of primary while debugging.
    else:
        for event in priDocIds:
            try:
                results = searchDomain(event)
                app.logger.debug(f"Results for processing AF lookup events " +
                                 f"{results}")
            except Exception as e:
                app.logger.error(f"Exception recieved processing document " +
                                 f"{event['document']}: {e}")
        for event in secDocIds:
            try:
                results = searchDomain(event)
                app.logger.debug(f"Results for processing AF lookup events " +
                                 f"{results}")
            except Exception as e:
                app.logger.error(f"Exception recieved processing document " +
                                 f"{event['document']}: {e}")



def searchDomain(event):
    '''
    Receives the ID of the event doc and gets the domain to search for
    from that doc.  Calls getDomainDoc() and looks at the known tags
    for the domain (if they exist).  Then calls assessTags() to determine
    the most probable campaign/actor/malware for the given set of tags.
    Writes that info to the event doc and updates it using the class save()
    method.
    '''
    processedValue = 0
    eventID = event['document']
    eventIndex = event['index']
    eventDomainName = event['domain_name']
    
    try:
        app.logger.debug(f"calling getDomainDoc() for {eventDomainName}")
        domainDoc = getDomainDoc(eventDomainName)
        app.logger.debug(f"domainDoc is {domainDoc}")

        if "NULL" in domainDoc:
            app.logger.warning(f"Unable to process event {eventID} beacause" +
                               f" of problem with domain-doc for" + 
                               f" {eventDomainName}")
        else:
            app.logger.debug(f"Assessing tags for domain-doc {domainDoc.name}")
            
            #  Set dummy info if no tags were found
            if (domainDoc.tags == None) or ("2000-01-01T00:00:00" in str(domainDoc.tags)):
                eventTag = {'tag_name': 'No tags found for domain',
                            'public_tag_name': 'No tags found for domain',
                            'tag_class': 'No tags found for domain',
                            'sample_date': '2000-01-01T00:00:00',
                            'file_type': 'NA',
                            'confidence_level': 0}
                processedValue = 55
            else:
                eventTag = assessTags(domainDoc.tags)
                processedValue = 1

            try:
                eventDoc = DNSEventDoc.get(id=eventID,index=eventIndex)
                eventDoc.SFN.event_type = "DNS"
                eventDoc.SFN.tag_name = eventTag['tag_name']
                eventDoc.SFN.public_tag_name = eventTag['public_tag_name']
                eventDoc.SFN.tag_class = eventTag['tag_class']
                eventDoc.SFN.tag_group = eventTag['tag_group']
                eventDoc.SFN.confidence_level = eventTag['confidence_level']
                eventDoc.SFN.sample_date = eventTag['sample_date']
                eventDoc.SFN.file_type = eventTag['file_type']
                eventDoc.SFN.tag_description = eventTag['description']
                eventDoc.SFN.updated_at = datetime.datetime.now()
                eventDoc.SFN.processed = processedValue
                eventDoc.save(id=eventID,index=eventIndex)
                
                app.logger.debug(f"Saved event doc with the following data:" +
                                f" {eventDoc}")
                
                return (f"{eventID} save: SUCCESS")
            
            except TransportError as te:
                app.logger.error(f"Transport Error working with {eventID}:" +
                                f" {te.info} ")
                return (f"{eventID} save: FAIL")
            except Exception as e:
                app.logger.error(f"Unable to work with event doc {eventID} - {e}")
                return (f"{eventID} save: FAIL")

    except Exception as e:
                app.logger.error(f"Unable to work with event doc {eventID} - {e}")
                return (f"{eventID} save: FAIL")



def main():
    processDNS()


if __name__ == "__main__":
    main()
