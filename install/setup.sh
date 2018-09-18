#!/usr/bin/env bash
# Push the ElasticSearch index mappings into the ElasticSearch DB
# NOTE: If you are using something other than the default install, you may need
# change the elasticsearch settings below to your IP address
printf "$(tput setaf 6)Installing index mappings into ElasticSearch$(tput sgr 0)\n"
printf "\n$(tput setaf 6)Installing af-details mapping$(tput sgr 0)\n"
curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/af-details/' -d @../infra/elasticsearch/mappings/af-details.json
printf "\n\n$(tput setaf 6)Installing threat mapping$(tput sgr 0)\n"
curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/_template/threat?pretty' -d @../infra/elasticsearch/mappings/threat_template_mapping.json
printf "\n$(tput setaf 6)Installing domain detail mapping$(tput sgr 0)\n"
curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/sfn-domain-details/' -d @../infra/elasticsearch/mappings/sfn-domain-details.json
printf "\n\n$(tput setaf 6)Installing tag mapping$(tput sgr 0)\n"
curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/sfn-tag-details/' -d @../infra/elasticsearch/mappings/sfn-tag-details.json
printf "\n\n$(tput setaf 6)Updating number of replicas to 0$(tput sgr 0)\n"
curl -XPUT -H'Content-Type: application/json' 'elasticsearch:9200/_settings' -d '{"index" : {"number_of_replicas" : 0}}'
# The traffic mappings are not installed by default - but here is the command if you want it
# curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/_template/traffic?pretty' -d @../infra/elasticsearch/mappings/traffic_template_mapping.json

# Set up the Elasticsearch heap size
HEAP_SIZE=8g
EXPORT_LINE="export ES_HEAP_SIZE=${HEAP_SIZE}"
printf "\n\n$(tput setaf 6)Setting ElasticSearch heap size to 8GB in environment$(tput sgr 0)\n"
# Check to see if the env var is already set in the .bashrc, if it is just 
# force it in the .bashrc to our setting here, if not, add it.  
grep ES_HEAP_SIZE ~/.bashrc
if [ $? == 0 ]; then
    unset ES_HEAP_SIZE
    echo "Found pre-set heap size, changing to ${HEAP_SIZE}"
    sed -i -E "s/(.+ES_HEAP_SIZE.+)/${EXPORT_LINE}/g" ~/.bashrc
else
    echo "export ES_HEAP_SIZE=${HEAP_SIZE}" >>~/.bashrc
fi    

# Source the .bashrc so the heap size setting is in the env
echo "Reading environment"
source ~/.bashrc
grep "export ES_HEAP_SIZE=${HEAP_SIZE}" ~/.bashrc
if [ $? == 0 ]; then
    echo "$(tput setaf 2)$(tput bold)The ElasticSearch heap size has been set in the .bashrc file"
    echo "For the environment to have the appropriate settings, run 'source ~/.bashrc'$(tput sgr 0)"
else
    echo "$(tput set af1)$(tput bold)You may need to edit the .bashrc and manually put" 
    echo "'export ES_HEAP_SIZE=${HEAP_SIZE}' in it to set the heap size.$(tput sgr 0)"
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
