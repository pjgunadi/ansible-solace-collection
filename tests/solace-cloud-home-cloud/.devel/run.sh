#!/usr/bin/env bash
# Copyright (c) 2022, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

scriptDir=$(cd $(dirname "$0") && pwd);
scriptName=$(basename $(test -L "$0" && readlink "$0" || echo "$0"));
projectHome=${scriptDir%/ansible-solace-collection/*}
if [[ ! $projectHome =~ "ansible-solace-collection" ]]; then
  projectHome=$projectHome/ansible-solace-collection
fi
export PROJECT_HOME=$projectHome


ansibleSolaceTests=(
  "solace-cloud-service"
)
export ANSIBLE_SOLACE_TESTS="${ansibleSolaceTests[*]}"

# solace cloud broker
  export INVENTORY_FILE="$projectHome/test-runner/files/solace-cloud-account.inventory.yml"

# US home cloud
  export SOLACE_CLOUD_API_TOKEN_US=$SOLACE_CLOUD_API_TOKEN_ALL_PERMISSIONS
# AU home cloud permissions
  export SOLACE_CLOUD_API_TOKEN_AU=$SOLACE_CLOUD_API_TOKEN_ALL_PERMISSIONS_SOLACE_AU


export CLEAN_WORKING_DIR=False

export LOG_DIR=$scriptDir/logs
mkdir -p $LOG_DIR
rm -rf $LOG_DIR/*

export ANSIBLE_LOG_PATH="$LOG_DIR/ansible.log"
export ANSIBLE_DEBUG=False
export ANSIBLE_VERBOSITY=3
# logging: ansible-solace
export ANSIBLE_SOLACE_LOG_PATH="$LOG_DIR/ansible-solace.log"
export ANSIBLE_SOLACE_ENABLE_LOGGING=True

export RUN_FG=true
# export RUN_FG=false

../_run.sh

###
# The End.
