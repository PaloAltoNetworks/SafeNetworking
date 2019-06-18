import time
import requests

from ast import literal_eval
from datetime import datetime
from multiprocessing.dummy import Pool
from elasticsearch import TransportError, ConnectionError, NotFoundError
from elasticsearch_dsl import Search

from project import app
from project.lib.sfnutils import getLatestTime, processTag
from project.iot.iot import IoTEventDoc, IoTDetailsDoc

def getExternalIoTDBUpdate(gapTime):
    '''
    Call the IoT HoneyPot DB server and retrieve all records since 
    gapTime minutes ago
    '''
    hpQuery = (f"{app.config['IOT_DB_URL']}/query_sfn_ip?gap={gapTime}")
    #hpQuery = (f"{app.config['IOT_DB_URL']}/query_sfn_ip?gap=100")
    app.logger.info(f"Sending query {hpQuery}")
    try:
        queryResponse = requests.get(url=hpQuery)
        if queryResponse.status_code == 200:
            app.logger.debug(f"Response from IoT HP query {queryResponse.text}")
            return literal_eval(queryResponse.text)
        else:
            raise Exception(f"Request to external IoT DB resulted in a status "
                            f"return of {queryResponse.status_code}")
    except Exception as e:
        app.logger.error(f"Trying to query IoT HoneyPot DB resulted in error {e}")
    

def __normalizeFamilyInfo(familyInfo):
        '''
        Private function used to normalize the family name since nobody can 
        agree on the actual name and it's different everywhere
        :returns: normalized family name AND the Unit42 version of same
        '''
        if (familyInfo['family'] == 'mirai') and (familyInfo['filetype'] == "elf"):
            newFamily = "Unit42.ELFMirai"
            newPubFamily = "ELFMirai"
        elif (familyInfo['family'] == 'frs') and (familyInfo['filetype'] == "elf"):
            newFamily = "Unit42.FRS_Ransomware"
            newPubFamily = "FRS_Ransomware"
        elif (familyInfo['family'] == 'xorddos') and (familyInfo['filetype'] == "elf"):
            newFamily = "Commodity.XorDDoS"
            newPubFamily = "XorDDoS"
        elif (familyInfo['family'] == 'coinminer') and (familyInfo['filetype'] == "elf"):
            newFamily = "Commodity.Coinminer"
            newPubFamily = "Coinminer"
        elif (familyInfo['family'] == 'ganiw') and (familyInfo['filetype'] == "elf"):
            newFamily = "Unit42.Ganiw"
            newPubFamily = "Ganiw"
        elif (familyInfo['family'] == 'ddostf') and (familyInfo['filetype'] == "elf"):
            newFamily = "Unit42.DDoSTF"
            newPubFamily = "DDoSTF"
        else:
            newFamily = "Unit42." + familyInfo['family']
            newPubFamily = familyInfo['family']
        
        return newFamily,newPubFamily


def normalizeIoTData(updateDict):
    '''
    Normalizes the data to be pushed to the DB.  The original data set that we
    get from the IoT HoneyPot DB is a dictionary with a list of dictionaries of 
    embedded lists of strings that look like dictionaries.  Sorta like Inception
    but with no other reason than "Just wanted to see if I could do it" or 
    something.  This just turns it all into a dictionary that we can use. 
    '''

    iotList = []
    normalizedData = {}
    
    for item in updateDict['data']:
        normalizedData['id'] = item['id']  
        normalizedData['ip'] = item['ip']
        normalizedData['time'] = item['time']
        familyInfo = literal_eval(item['familyinfo'])
        normalizedData['filetype'] = familyInfo['filetype']
        normalizedData['tag_name'],normalizedData['public_tag_name'] = __normalizeFamilyInfo(familyInfo) 
        tagObject = processTag(normalizedData['tag_name'])
        item.update({'tag_class': tagObject[2]})
        item.update({'tag_group_name': tagObject[3]})
        item.update({'description': tagObject[4]})
        normalizedData['tag_class'] = item['tag_class']
        normalizedData['tag_group_name'] = item['tag_group_name']
        normalizedData['description'] = item['description']
        iotList.append(dict(normalizedData))
        
    normalizedDict = {'data': iotList}
    return(normalizedDict)
        

def updateLocalIoTDB(updateDict):
    '''
    Push the objects in the updateDict as new documents in our ES DV
    :param updateDict: dictionary of IoT updates retrived from server
    :returns: SUCCESS
    '''
    
    retType = "SUCCESS"

    for item in updateDict['data']:
        try:
            iotDoc = IoTDetailsDoc.get(id=item['id'])
        except NotFoundError as nfe:
            app.logger.info(f"No IoT info doc found for {item['ip']} - creating")
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
            iotDoc.filetype = item['filetype']
            iotDoc.tag_name = item['tag_name']
            iotDoc.tag_class = item['tag_class']
            iotDoc.tag_description = item['description']
            iotDoc.tag_group_name = item['tag_group_name']
            iotDoc.public_tag_name = item['public_tag_name']
            iotDoc.save()
        except Exception as e:
            app.logger.error(f"Unable to save IoT DB document because of error: {e}")
            retType = "FAIL"

    return retType


def processIoT():
    '''
    Retrieve updates from the IoT Honeypot DB and add to SFN DB
    '''

    iotIndex = 'sfn-iot-details'
    dbUpdate = 'NA'
    app.logger.debug(f"Retrieving changes from IoT Honepot DB")
    
    # Get the last update and calculate the time diff for the API call
    try:
        latestTime = round(getLatestTime(iotIndex))
        app.logger.debug(f"Latest time diff for IoT DB is calculated as {latestTime} minutes")
    except Exception as e:
        timeStamp = datetime.strptime('2019-02-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        latestTime = round((datetime.utcnow() - timeStamp).total_seconds() / 60.0)

    # Get DB Update via API
    
    try:
        updateDict = getExternalIoTDBUpdate(latestTime)
        if updateDict:
            if not updateDict['data']:
                app.logger.info(f"Update from IoT DB is empty, nothing to do, sleeping")
            else:    
                #app.logger.debug(f"Latest update from IoT DB is {updateDict}")
                normalizedDict = normalizeIoTData(updateDict)
                dbUpdate = updateLocalIoTDB(normalizedDict)
                # Return success/fail
                if "SUCCESS" in dbUpdate:
                    app.logger.info("Successfully updated IoT DB")
                else:
                    app.logger.error("Unable to update IoT DB")      
    except Exception as e:
        app.logger.error(f"{e}")            

def main():
    processIoT()


if __name__ == "__main__":
    main()
