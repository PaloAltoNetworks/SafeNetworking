#!/usr/bin/env bash

# Check to see if we need to install the gtp DB.
installGTP=0

for arg in "$@"
do
    if [ "$arg" == "--gtp" ] || [ "$arg" == "-g" ]
    then
        installGTP=1
    fi
done

################################################################################
#                          SYSTEM SETUP
################################################################################

# Figure out who we are so we write the correct paths
userName=$(echo $SUDO_USER)
userHome=$(eval echo "~$userName" )
printf "\n>>> $(tput setaf 3)Setting up for user $userName in $userHome directory $(tput sgr 0)\n"

# Create backup directory and make world writeable so elasticsearch can use it.
if [ ! -d "$userHome/es_backup" ]; then
  install -d -m 0777 -o $userName -g $(id -gn $userName) $userHome/es_backup
fi

#if [ ! -d "$userHome/safe-networking/env" ]; then
#  cd $userHome/safe-networking
#  python3.6 -m venv env
#  source env/bin/activate
#  pip install --upgrade pip
#  pip install -r requirements
#fi

################################################################################
#                       ELASTICSTACK SETUP
################################################################################
#                       ELASTICSEARCH SETUP
#
# Copy over the config files that are needed for SFN to work in a PoC env
# First thing we do is 
printf "\n>>> $(tput setaf 6)Backing up elasticsearch config files$(tput sgr 0)"
find ./elasticsearch/config/elasticsearch_template.yml -exec sed "s#_USER_HOME_#$userHome#g" {} \; > ./elasticsearch/config/elasticsearch.yml 
cp /etc/elasticsearch/elasticsearch.yml /etc/elasticsearch/elasticsearch.yml.$(date +%F_%R)
cp /etc/elasticsearch/jvm.options /etc/elasticsearch/jvm.options.$(date +%F_%R)
printf " - COMPLETE\n"
printf ">>> $(tput setaf 6)Installing new elasticsearch config files$(tput sgr 0)"
cp ./elasticsearch/config/elasticsearch.yml /etc/elasticsearch/elasticsearch.yml
cp ./elasticsearch/config/jvm.options /etc/elasticsearch/jvm.options
printf " - COMPLETE\n"
printf ">>> $(tput setaf 6)Installing logstash pipelines and config files$(tput sgr 0)"
if [ ! -d "/etc/logstash/pipelines" ]; then
    install -d -m 0777 -o $userName -g $(id -gn $userName) /etc/logstash/pipelines 
fi
cp ./logstash/*.conf /etc/logstash/pipelines/
cp /etc/logstash/pipelines.yml /etc/logstash/pipelines.yml.$(date +%F_%R)
cp ./logstash/pipelines.yml /etc/logstash/pipelines.yml
cp /etc/logstash/logstash.yml /etc/logstash/logstash.yml.$(date +%F_%R)
cp ./logstash/logstash.yml /etc/logstash/logstash.yml
printf " - COMPLETE\n"
printf "\n>>> $(tput setaf 6)Backing up kibana config files$(tput sgr 0)"
cp /etc/kibana/kibana.yml /etc/kibana/kibana.yml.$(date +%F_%R)
printf " - COMPLETE\n"
printf ">>> $(tput setaf 6)Installing new kibana config files$(tput sgr 0)"
cp ./kibana/kibana.yml /etc/kibana/kibana.yml
printf " - COMPLETE\n"

printf "\n>>> $(tput setaf 6)Setting up ELK services$(tput sgr 0)\n"
printf "  >>> $(tput setaf 6)Setting up Elasticsearch auto-start$(tput sgr 0)\n"
/bin/systemctl daemon-reload
/bin/systemctl enable elasticsearch.service
/bin/systemctl restart elasticsearch.service

# sleep for 10 seconds so ES can come up
printf "\t- Waiting 10 seconds for Elasticsearch to start\n"
sleep 10

curl 127.0.0.1:9200 >/dev/null 2>&1
if [ $? -eq 0 ]; then
    printf "\t* $(tput setaf 10)Elasticsearch is up and running$(tput sgr 0)\n"
else
    printf "\t- Elasticsearch not up yet, waiting 15 more seconds\n"
    sleep 15
    curl 127.0.0.1:9200 >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        printf "\t* $(tput setaf 10)Elasticsearch is up and running$(tput sgr 0) - COMPLETE\n"
    else
        printf "\t* $(tput setaf 9)Elasticsearch is NOT running - EXITING$(tput sgr 0)\n"
        exit 7
    fi
fi

printf "  >>> $(tput setaf 6)Setting up logstash auto-start$(tput sgr 0)\n"
/bin/systemctl daemon-reload
/bin/systemctl enable logstash.service
/bin/systemctl restart logstash.service
# sleep for 30 seconds so logstash can come up
printf "\t- Waiting 30 seconds for Logstash to start\n"
sleep 30
(echo >/dev/tcp/localhost/5514) >/dev/null 2>&1
if [ $? -eq 0 ]; then
    printf "\t* $(tput setaf 10)Logstash is up and running on port 5514"
    printf "$(tput sgr 0) - COMPLETE\n"
else
    printf "\t- Logstash not up yet, waiting 30 more seconds\n"
    sleep 30
    (echo >/dev/tcp/localhost/5514) >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        printf "\t* $(tput setaf 10)Logstash is up and running on port 5514"
        printf "$(tput sgr 0) - COMPLETE\n"
    else
        printf "\t* $(tput setaf 9)Logstash is NOT running $(tput sgr 0)"
        printf " - view /var/log/logstash/logstash-plain.log for troubleshooting\n"
    fi
fi

printf "  >>> $(tput setaf 6)Setting up kibana auto-start$(tput sgr 0)\n"
/bin/systemctl daemon-reload
/bin/systemctl enable kibana.service
/bin/systemctl restart kibana.service
printf "  >>> Kibana service installed. To test, goto http://<your-ip> to verify\n"



# Push the ElasticSearch index mappings into the ElasticSearch DB
# NOTE: If you are using something other than the default install, you may need
# change the elasticsearch settings below to your IP address
#
printf "$(tput setaf 6)Installing index mappings into ElasticSearch$(tput sgr 0)\n"
printf "\n$(tput setaf 6)Installing af-details mapping$(tput sgr 0)\n"
curl -XPUT -H'Content-Type: application/json' \
    'http://localhost:9200/af-details/' \
    -d @./elasticsearch/mappings/af-details.json

printf "\n\n$(tput setaf 6)Installing threat mapping$(tput sgr 0)\n"
curl -XPUT -H'Content-Type: application/json' \
    'http://localhost:9200/_template/threat?pretty' \
    -d @./elasticsearch/mappings/threat_template_mapping.json

printf "\n$(tput setaf 6)Installing domain detail mapping$(tput sgr 0)\n"
curl -XPUT -H'Content-Type: application/json' \
    'http://localhost:9200/sfn-domain-details/' \
    -d @./elasticsearch/mappings/sfn-domain-details.json

printf "\n\n$(tput setaf 6)Installing tag mapping$(tput sgr 0)\n"
curl -XPUT -H'Content-Type: application/json' \
    'http://localhost:9200/sfn-tag-details/' \
    -d @./elasticsearch/mappings/sfn-tag-details.json

printf "\n\n$(tput setaf 6)Updating number of replicas to 0$(tput sgr 0)\n"
curl -XPUT -H'Content-Type: application/json' 'localhost:9200/_settings' \
    -d '{"index" : {"number_of_replicas" : 0}}'

################################################################################
# The traffic mappings are not installed by default
# but here is the command if you want it  (not recommended)
# curl -XPUT -H'Content-Type: application/json' \
#      'http://localhost:9200/_template/traffic?pretty' \
#      -d @./elasticsearch/mappings/traffic_template_mapping.json

################################################################################

# Load the GTP and IoT databases for enrichment
if [ installGTP ]
    printf "\n\n$(tput setaf 6)Installing GTP Event Code Documents$(tput sgr 0)\n"
    then
        for file in `ls $userHome/safe-networking/install/elasticsearch/lookup_data/gtp/*.csv`
            do
                ./sfn load $file test-gtp-codes
            done
fi


################################################################################
# THE FOLLOWING IS DEPRECATED AND THE SFN APPLICATION WILL NO LONGER BE RUN AS
# A SERVICE IN FUTURE RELEASES.  IT IS LEFT HERE IN CASE YOU WANT TO TRY AND 
# RUN IT AS A SERVICE, BUT IT IS NOT SUPPORTED
################################################################################
# This sets up the automatic startup of SFN if the system reboots.  It also gives
# the ability to control SafeNetworking as a service using the systemctl and
# service commands
# INSTALL_DIR="$(dirname `pwd`)"
# START_FILE=$INSTALL_DIR/install/sfn/sfn.sh
# echo "Creating SafeNetworking startup file $START_FILE"
# echo "...."
# echo "#!/bin/sh -" >$START_FILE
# echo "# SafeNetworking startup file" >>$START_FILE
# echo "cd $INSTALL_DIR" >>$START_FILE
# echo "$INSTALL_DIR/env/bin/python $INSTALL_DIR/sfn" >>$START_FILE
# echo ""
# echo "Moving startup file to /usr/local/bin -->"
# echo "...."
# sudo cp $START_FILE /usr/local/bin/sfn.sh
# sudo chmod 755 /usr/local/bin/sfn.sh
# echo ""
# echo "Copying sfn.service to /etc/systemd/system -->"
# echo "...."
# sudo cp $INSTALL_DIR/install/sfn/sfn.service /etc/systemd/system/sfn.service
# echo ""
# sudo chmod 644 /etc/systemd/system/sfn.service
# echo "Enabling and starting the SafeNetworking Service - this may take a minute"
# sudo systemctl daemon-reload
# sudo systemctl enable sfn.service
# sudo systemctl start sfn.service
# sudo systemctl status sfn.service
