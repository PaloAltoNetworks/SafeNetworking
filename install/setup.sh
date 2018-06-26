# Push the ElasticSearch index mappings into the ElasticSearch DB
# NOTE: If you are using something other than the default install, you may need
# change the localhost settings below to your IP address
echo "Installing index mappings into ElasticSearch"
curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/af-details/' -d @../infra/elasticsearch/mappings/af-details.json
curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/_template/traffic?pretty' -d @../infra/elasticsearch/mappings/traffic_template_mapping.json
curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/_template/threat?pretty' -d @../infra/elasticsearch/mappings/threat_template_mapping.json
curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/sfn-domain-details/' -d @../infra/elasticsearch/mappings/sfn-domain-details.json
curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/sfn-tag-details/' -d @../infra/elasticsearch/mappings/sfn-tag-details.json
curl -XPUT -H'Content-Type: application/json' 'localhost:9200/_settings' -d '{"index" : {"number_of_replicas" : 0}}'

echo "\n"

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
