#!/usr/bin/env bash

################################################################################
#                          SYSTEM SETUP
################################################################################
# Create backup directory and make world writeable so elasticsearch can use it.
install -d -m 0777 -o pan -g admin /home/pan/es_backup

################################################################################
#                           ELASTICSTACK SETUP
################################################################################
#                       ELASTICSEARCH SETUP
#
# Copy over the config files that are needed for SFN to work in a PoC env
printf "\n>>> $(tput setaf 6)Backing up elasticsearch config files$(tput sgr 0)"
cp /etc/elasticsearch/elasticsearch.yml /etc/elasticsearch/elasticsearch.yml.orig
cp /etc/elasticsearch/jvm.options /etc/elasticsearch/jvm.options.orig
printf " - COMPLETE\n"
printf ">>> $(tput setaf 6)Installing new elasticsearch config files$(tput sgr 0)"
cp ./install/elasticsearch/config/elasticsearch.yml /etc/elasticsearch/elasticsearch.yml
cp ./install/elasticsearch/config/jvm.options /etc/elasticsearch/jvm.options
printf " - COMPLETE\n"
printf ">>> $(tput setaf 6)Installing logstash config files$(tput sgr 0)"
cp ./install/logstash/pan-sfn.conf /etc/logstash/conf.d/pan-sfn.conf
printf " - COMPLETE\n"
printf "\n>>> $(tput setaf 6)Backing up kibana config files$(tput sgr 0)"
cp /etc/kibana/kibana.yml /etc/kibana/kibana.yml.orig
printf " - COMPLETE\n"
printf ">>> $(tput setaf 6)Installing new kibana config files$(tput sgr 0)"
cp ./install/kibana/kibana.yml /etc/kibana/kibana.yml
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
    printf "\t- Elasticsearch not up yet, waiting 10 more seconds\n"
    sleep 10
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
curl -XPUT -H'Content-Type: application/json' 'elasticsearch:9200/_settings' \
    -d '{"index" : {"number_of_replicas" : 0}}'

################################################################################
# The traffic mappings are not installed by default
# but here is the command if you want it  (not recommended)
# curl -XPUT -H'Content-Type: application/json' \
#      'http://localhost:9200/_template/traffic?pretty' \
#      -d @./elasticsearch/mappings/traffic_template_mapping.json


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
