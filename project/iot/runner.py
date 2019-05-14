import time
import datetime

from multiprocessing.dummy import Pool
from elasticsearch import TransportError, ConnectionError
from elasticsearch_dsl import Search

from project import app
from project.iot.iot import IoTEventDoc


def processIoT():
    '''
    Retrieve updates from the IoT Honeypot DB and add to SFN DB
    '''

    # This should be true only once per run of the SFN code.  At startup, 
    # delete everything in the IoT DB and retrieve the whole DB from the 
    # server.  
    if app.config["IOT_BOOTSTRAP"] == True:    # Multiprocess the primary keys
        app.logger.debug(f"Dumping local IoT DB")

    else:
        app.logger.debug(f"Retrieving changes from IoT Honepot DB")    
        

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
            app.logger.error(f"Unable to process event {eventID} beacause" +
                               f" of problem with domain-doc for" + 
                               f" {eventDomainName}")
        else:
            app.logger.debug(f"Assessing tags for domain-doc {domainDoc.name}")
            
            #  Set dummy info if no tags were found
            if (domainDoc.tags == None) or ("2000-01-01T00:00:00" in str(domainDoc.tags)):
                app.logger.debug(f"No tags found for domain {domainDoc.name}")
                eventTag = {'tag_name': 'No tags found for domain',
                            'public_tag_name': 'No tags found for domain',
                            'tag_class': 'No tags found for domain',
                            'tag_group': 'No tags found for domain',
                            'description': 'No tags found for domain',
                            'sample_date': '2000-01-01T00:00:00',
                            'file_type': 'NA',
                            'confidence_level': 0}
                processedValue = 55
            else:
                app.logger.debug(f"calling assessTags({domainDoc.tags})")
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
