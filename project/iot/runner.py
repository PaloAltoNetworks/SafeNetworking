import time
import datetime

from multiprocessing.dummy import Pool
from elasticsearch import TransportError, ConnectionError
from elasticsearch_dsl import Search

from project import app
from project.utils.sfnutils import getLatestTime
from project.iot.iot import IoTEventDoc



def processIoT():
    '''
    Retrieve updates from the IoT Honeypot DB and add to SFN DB
    '''

    app.logger.debug(f"Retrieving changes from IoT Honepot DB")
    
    # Get the last update and calculate the time diff for the API call
    latestTime = getLatestTime("sfn-iot-details")

    # Get DB Update

    # Store the Update

    # Return success/fail        
        



def main():
    processIoT()


if __name__ == "__main__":
    main()
