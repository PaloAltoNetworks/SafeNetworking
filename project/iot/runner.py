import time
import requests
import datetime

from ast import literal_eval
from multiprocessing.dummy import Pool
from elasticsearch import TransportError, ConnectionError, NotFoundError
from elasticsearch_dsl import Search

from project import app
from project.lib.sfnutils import getLatestTime
from project.iot.iot import IoTEventDoc, IoTDetailsDoc

def getIoTDBUpdate(gapTime):
    '''
    Call the IoT HoneyPot DB server and retrieve all records since 
    gapTime minutes ago
    '''
    hpQuery = (f"{app.config['IOT_DB_URL']}/query_sfn_ip?gap={gapTime}")
    app.logger.info(f"Sending query to {hpQuery}")
    try:
        queryResponse = requests.get(url=hpQuery)
        app.logger.debug(f"Here is the response {queryResponse.text}")
        return literal_eval(queryResponse.text)
    except Exception as e:
        app.logger.error(f"Trying to query IoT HoneyPot DB resulted in error {e}")
    

def updateLocalIoTDB(updateDict):
    '''
    Push the objects in the updateDict as new documents in our ES DV
    :param updateDict: dictionary of IoT updates retrived from server
    :returns: SUCCESS
    '''
  
    for item in updateDict['data']:
        try:
            iotDoc = IoTDetailsDoc.get(id=item['id'])
        except NotFoundError as nfe:
            app.logger.info(f"No IoT doc is not found for {item['ip']}- creating")
            iotDoc = IoTDetailsDoc(meta={'id': item['id']})
        except TransportError as te:
            app.logger.error(f"Unable to access DB because of {te}")
        except Exception as e:
            app.logger.error(f"Unable to access DB because of {e}")

        try:
            app.logger.debug(f"Updating sfn-iot-details with {item}")
            iotDoc.meta.id = item['id']
            iotDoc.ip = item['ip']
            iotDoc.time = item['time']
            iotDoc.familyinfo = item['familyinfo']
            iotDoc.save()
        except Exception as e:
            app.logger.error(f"Unable to save IoT DB document because of error {e}")

    return "SUCCESS"

def processIoT():
    '''
    Retrieve updates from the IoT Honeypot DB and add to SFN DB
    '''

    iotIndex = "sfn-iot-details"
    dbUpdate = "NA"
    app.logger.debug(f"Retrieving changes from IoT Honepot DB")
    
    # Get the last update and calculate the time diff for the API call
    latestTime = round(getLatestTime(iotIndex))
    app.logger.debug(f"Latest time is calculated as {latestTime}")
    # Get DB Update via API
    updateDict = getIoTDBUpdate(latestTime)
    # Store the Update
    dbUpdate = updateLocalIoTDB(updateDict)
    # Return success/fail
    if "SUCCESS" in dbUpdate:
        app.logger.info("Successfully updated IoT DB")
    else:
        app.logger.error("Unable to update IoT DB")      
        



def main():
    processIoT()


if __name__ == "__main__":
    main()
