#!/usr/bin/env bash
# (c) 2020 Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

scriptDir=$(cd $(dirname "$0") && pwd);
scriptName=$(basename $(test -L "$0" && readlink "$0" || echo "$0"));
export testTargetGroup=${scriptDir##*/}
scriptLogName="$testTargetGroup.$scriptName"
if [ -z "$PROJECT_HOME" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: PROJECT_HOME"; exit 1; fi
source $PROJECT_HOME/.lib/functions.sh

############################################################################################################################
# Environment Variables

  if [ -z "$LOG_DIR" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: LOG_DIR"; exit 1; fi
  if [ -z "$RUN_FG" ]; then echo ">>> XT_ERROR: - $scriptLogName - missing env var: RUN_FG"; exit 1; fi

  if [ -z "$ANSIBLE_SOLACE_TESTS" ]; then
    export ANSIBLE_SOLACE_TESTS=(
      # "broker-cert"
      "setup"
      "solace_jndi"
      "solace_replay"
      "solace_get_list"
      "solace_service_auth"
      "solace_get_available"
      "solace_auth"
      "solace_oauth"
      "solace_facts"
      "solace_vpn"
      "solace_acl_profile"
      "solace_rdp"
      "solace_cert_authority"
      "solace_queue"
      "solace_client_username"
      "solace_mqtt"
      "solace_topic_endpoint"
      "solace_get_vpn_clients"
      "solace_client_profile"
      "teardown"
    )
  fi

##############################################################################################################################
# Prepare

export WORKING_DIR="$scriptDir/tmp"
mkdir -p $WORKING_DIR
if [ -z "$CLEAN_WORKING_DIR" ]; then rm -rf $WORKING_DIR/*; fi

##############################################################################################################################
# Run

  for ansibleSolaceTest in ${ANSIBLE_SOLACE_TESTS[@]}; do

      runScript="$scriptDir/$ansibleSolaceTest/_run.sh"

      echo ">>> TEST: $testTargetGroup/$ansibleSolaceTest"

      if [[ "$RUN_FG" == "false" ]]; then
        $runScript > $LOG_DIR/$testTargetGroup.$ansibleSolaceTest._run.sh.out 2>&1
      else
        $runScript
      fi
      code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - code=$code - runScript='$runScript' - $scriptLogName"; exit 1; fi

  done

###
# The End.
