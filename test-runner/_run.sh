#!/usr/bin/env bash
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

scriptDir=$(cd $(dirname "$0") && pwd);
scriptName=$(basename $(test -L "$0" && readlink "$0" || echo "$0"));
testRunner="test-runner"
scriptLogName="$testRunner.$scriptName"
if [ -z "$PROJECT_HOME" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: PROJECT_HOME"; exit 1; fi
source $PROJECT_HOME/.lib/functions.sh

############################################################################################################################
# Environment Variables

  if [ -z "$SOLACE_CLOUD_API_TOKEN_ALL_PERMISSIONS" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: SOLACE_CLOUD_API_TOKEN_ALL_PERMISSIONS"; exit 1; fi
  if [ -z "$SOLACE_CLOUD_API_TOKEN_RESTRICTED_PERMISSIONS" ]; then echo ">>> ERROR: - $scriptLogName - missing env var: SOLACE_CLOUD_API_TOKEN_RESTRICTED_PERMISSIONS"; exit 1; fi
  if [ -z "$LOG_DIR" ]; then echo ">>> ERROR: - $scriptName - missing env var: LOG_DIR"; exit 1; fi

##############################################################################################################################
# Settings
export RUN_FG=false
baseLogDir=$LOG_DIR
testsBaseDir="$PROJECT_HOME/tests"
localBrokerInventoryFile="$PROJECT_HOME/test-runner/files/local.broker.inventory.yml"
localBrokerDockerComposeFile="$PROJECT_HOME/test-runner/files/PubSubStandard_singleNode.yml"
solaceCloudAccountInventoryFile="$PROJECT_HOME/test-runner/files/solace-cloud-account.inventory.yml"
brokerDockerImages=(
  "solace/solace-pubsub-standard:9.3.1.28"
  # "solace/solace-pubsub-standard:9.5.0.30"
  # "solace/solace-pubsub-standard:9.6.0.32"
  # "solace/solace-pubsub-standard:9.6.0.38"
  # "solace/solace-pubsub-standard:9.7.0.29"
  "solace/solace-pubsub-standard:latest"
)

#################################################################################################################################################
ansibleSolaceTestTargetGroup="single_broker"
#################################################################################################################################################

  for brokerDockerImage in ${brokerDockerImages[@]}; do

    export LOG_DIR="$baseLogDir/$ansibleSolaceTestTargetGroup/$brokerDockerImage"
    mkdir -p $LOG_DIR

    export BROKER_TYPE="local"
    export INVENTORY_FILE=$localBrokerInventoryFile
    export BROKER_DOCKER_IMAGE=$brokerDockerImage
    export LOCAL_BROKER_INVENTORY_FILE=$localBrokerInventoryFile
    export BROKER_DOCKER_COMPOSE_FILE=$localBrokerDockerComposeFile

    echo "##############################################################################################################"
    echo "# Test target group: $ansibleSolaceTestTargetGroup($BROKER_TYPE, $brokerDockerImage)"

    runScript="$testsBaseDir/$ansibleSolaceTestTargetGroup/_run.sh"
    $runScript
    code=$?; if [[ $code != 0 ]]; then echo ">>> ERROR - code=$code - runScript='$runScript' - $scriptLogName"; exit 1; fi

  done

  export LOG_DIR="$baseLogDir/$ansibleSolaceTestTargetGroup/solace_cloud"
  mkdir -p $LOG_DIR
  export BROKER_TYPE="solace_cloud"
  export INVENTORY_FILE=$solaceCloudAccountInventoryFile
  export SOLACE_CLOUD_API_TOKEN=$SOLACE_CLOUD_API_TOKEN_ALL_PERMISSIONS

  echo "##############################################################################################################"
  echo "# test target group: $ansibleSolaceTestTargetGroup($BROKER_TYPE)"

  runScript="$testsBaseDir/$ansibleSolaceTestTargetGroup/_run.sh"
  $runScript
  code=$?; if [[ $code != 0 ]]; then echo ">>> ERROR - code=$code - runScript='$runScript' - $scriptLogName"; exit 1; fi

#################################################################################################################################################
ansibleSolaceTestTargetGroup="next_group"
#################################################################################################################################################




###
# The End.
