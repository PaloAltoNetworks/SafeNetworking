# project/__init__.py

import os
import logging
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_elasticsearch import Elasticsearch
from logging.handlers import RotatingFileHandler
from elasticsearch_dsl import connections

class SFNFormatter(logging.Formatter):
    width = 55
    datefmt='%Y-%m-%d %H:%M:%S'

    def format(self, record):
        cpath = f'{record.module}:{record.funcName}:[{record.lineno}]:{record.thread}'
        cpath = cpath[-self.width:].ljust(self.width)
        #record.message = record.getMessage()
        levelName = f"[{record.levelname}]"
        outputString = (f"{levelName:<10}: "
                       f"{self.formatTime(record, self.datefmt)} : {cpath} : "
                       f"{record.getMessage()}")

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if outputString[-1:] != "\n":
                outputString = outputString + "\n"
            outputString = outputString + record.exc_text
        return outputString


# Initialize the app for Flask
app = Flask(__name__)


# Set the configuration parameters that are used by the application.
# These values are overriden by the .panrc file located in the base directory
# for the application
#
# ---------- APPLICATION SETTINGS --------------
#
# Current version number of SafeNetworking
app.config['VERSION'] = "v4.0"
#
# When set to True, this slows down the logging by only processing 1 event at a
# time and allows us to see what is going on if there are bugs
app.config['DEBUG_MODE'] = False
#
# Flask setting for where session manager contains the info on the session(s)
app.config['SESSION_TYPE'] = "filesystem"
#
# Secret key needed by session setting above.
app.config['SECRET_KEY'] = "\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5"
#
# Sets the base directory for the application
app.config['BASE_DIR'] = os.path.abspath(os.path.dirname(__file__))
#
# Set the number of seconds for multi-threading to wait between processing calls
app.config['DNS_POOL_TIME'] = 5
app.config['URL_POOL_TIME'] = 10
app.config['AF_POOL_TIME'] = 600
app.config['IOT_POOL_TIME'] = 600
#
# Turn off DNS processing.
app.config["DNS_PROCESSING"] = True
# Turn off IoT processing.  
app.config["IOT_PROCESSING"] = False
# Turn off URL processing.  
app.config["URL_PROCESSING"] = False
#
# This is an internal flag that will probably never show up in the .panrc file
# It is used to slow execution when it is True
app.config['AF_POINTS_MODE'] = False
#
# Number of AF points left to slow down processing so we don't run out of points
# When it reaches this point, it sets the AF_POINTS_MODE to True and it slows
# execution to 1 event at a time.
app.config['AF_POINTS_LOW'] = 5000
#
# Number of AF points left to stop processing all together
app.config['AF_POINT_NOEXEC'] = 500
#
# Number of seconds to wait when AF_POINT_NOEXEC gets triggered.  This stops all
# app execution and checks the AF points total at the specified interval.  When
# the points total is higher than AF_POINT_NOEXEC it resumes execution.
app.config['AF_NOEXEC_CKTIME'] = 3600
#
# Set the number of processes to run the DNS module.  This cannot be more than
# 16 or it will kill the AF minute points.  The code will  take care of cases
# where it is greater than 16 and this should only be adjusted down (never up).
# Remember that DNS_POOL_COUNT and URL_POOL_COUNT have to share the total of 16.
# The application will check and throw an error (but it will still run) if the
# two settings together is more than 16.
app.config['DNS_POOL_COUNT'] = 16
#
# Set the number of processes to run the URL module.  This cannot be more than
# 16 or it will kill the AF minute points.  The code will  take care of cases
# where it is greater than 16 and this should only be adjusted down (never up)
app.config['URL_POOL_COUNT'] = 0
#
# When SafeNetworking is started, number of documents to read from the DB.  The
# larger the number, the longer this will take to catch up.
app.config['DNS_EVENT_QUERY_SIZE'] = 1000
app.config['IOT_EVENT_QUERY_SIZE'] = 1000
# app.config['SEC_PROCESS_QUERY_SIZE'] = 1000 - what the hell is this for?
#
# SafeNetworking caches domain info from AutoFocus.  This setting specifies, in
# days, how long the cache is ok.  If there is cached info on this domain and it
# is older than the setting, SFN will query AF and update as necessary and reset
# the cache "last_updated" setting in ElasticSearch.
app.config['DNS_DOMAIN_INFO_MAX_AGE'] = 30
#
# The Autofocus API isn't the speediest thing on the planet.  Usually, the most
# pertinent info is within the first couple of minutes of query time.  So, set
# this to drop out of the processing loop and stop waiting for the query to
# finish - which could take 20mins.  No lie....   This is set in minutes
app.config['AF_LOOKUP_TIMEOUT'] = 2
#
# The maximum percentage of the AF query we are willing to accept.  If, when we
# check the timer above, the value is greater than this percentage, we bail out
# of the loop.  The lower the number, the more likely that we may not get a
# result.  Though, usually, 2 minutes and 20 percent is enough to get at least
# the latest result.
app.config['AF_LOOKUP_MAX_PERCENTAGE'] = 20
#
# The maximum age for tag info.  This doesn't need to be updated as often as
# the domain or other items, but should be done periodically just in case..
# Setting is in days.
app.config['DOMAIN_TAG_INFO_MAX_AGE'] = 120
#
# Dictionary definition of confidence levels represented as max days and the
# level associated  - i.e. 3:80 would represent an 80% confidence level if the
# item is no more than 3 days old
app.config['CONFIDENCE_LEVELS'] = "{'15':90,'25':80,'40':70,'50':60,'60':50}"
#
#
# ------------------------------- LOGGING --------------------------------------
#
# Log level for Flask
app.config['FLASK_LOGGING_LEVEL'] = "ERROR"
#
# Set the system to automatically start with DEBUG on.  This changed in 3.6 as
# all installs are using DEBUG.
app.config['DEBUG'] = True
#
# Log level for the SafeNetworking application itself.  All files are written
# to log/sfn.log
app.config['LOG_LEVEL'] = "DEBUG"
#
# Size of Log file before rotating - in bytes
app.config['LOG_SIZE'] = 1000000000
#
# Number of log files to keep in log rotation
app.config['LOG_BACKUPS'] = 10
#
#
#
# ----------------------------- ELASTICSTACK -----------------------------------
#
# By default our ElasticStack is installed all on the same system
app.config['ELASTICSEARCH_HOST'] = "localhost"
app.config['ELASTICSEARCH_PORT'] = "9200"
app.config['ELASTICSEARCH_HTTP_AUTH'] = ""
app.config['KIBANA_HOST'] = "localhost"
app.config['KIBANA_PORT'] = "5601"
app.config['ELASTICSTACK_VERSION'] = "6.4"
#
#
#
# ------------------------------ FLASK -----------------------------------------
#
# By default Flask listens to all ports - we will only listen to localhost
# for security reasons, but keep the default port of 5000
app.config['FLASK_HOST'] = "localhost"
app.config['FLASK_PORT'] = 5000
#
#
#
# ----------------------------- MISCELLANEOUS ----------------------------------
#
app.config['AUTOFOCUS_API_KEY'] = "NOT-SET"
app.config['AUTOFOCUS_HOSTNAME'] = "autofocus.paloaltonetworks.com"
app.config['AUTOFOCUS_SEARCH_URL'] = "https://autofocus.paloaltonetworks.com/api/v1.0/samples/search"
app.config['AUTOFOCUS_RESULTS_URL'] = "https://autofocus.paloaltonetworks.com/api/v1.0/samples/results/"
app.config['AUTOFOCUS_TAG_URL'] = "https://autofocus.paloaltonetworks.com/api/v1.0/tag/"
app.config['IOT_DB_URL'] = "http://35.160.110.244:58888/api/v1"
#
#

# Set instance config parameters
app.config.from_pyfile('.panrc')
# Add bootstrap object for Flask served pages
bs = Bootstrap(app)
# Add Elasticsearch object for our instance of ES
es = Elasticsearch(f"{app.config['ELASTICSEARCH_HOST']}:{app.config['ELASTICSEARCH_PORT']}")
# Define the default Elasticsearch client
connections.create_connection(hosts=[app.config['ELASTICSEARCH_HOST']])

# Set up logging for the application - we may want to revisit this
# see issue #10 in repo
handler = RotatingFileHandler(f"{app.config['BASE_DIR']}/../log/sfn.log",
                            maxBytes=app.config['LOG_SIZE'],
                            backupCount=app.config['LOG_BACKUPS'])
sfnFormatter = SFNFormatter()
handler.setLevel(app.config["LOG_LEVEL"])
handler.setFormatter(sfnFormatter)
app.logger.addHandler(handler)


# Register blueprints
from project.views import sfn_blueprint
app.register_blueprint(sfn_blueprint)
