#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026, Solace Corporation
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_dmr_cluster_cert_matching_rule_condition
short_description: condition for a dmr cluster certificate matching rule
description:
- "Allows addition and removal of Condition Objects on a DMR Cluster Certificate Matching Rule."
- "A Condition is identified by its source and expression. Both form the object's identifier - to change a Condition, remove the old one and add a new one."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/dmrCluster/\
  createDmrClusterCertMatchingRuleCondition"
options:
  source:
    description: The name of the source of the Condition. Maps to 'source' in the API.
    required: true
    type: str
  expression:
    description: The expression to match against the source. Maps to 'expression' in the API.
    required: true
    type: str
  cert_matching_rule_name:
    description: The name of the Certificate Matching Rule. Maps to 'certMatchingRuleName' in the API.
    required: true
    type: str
  dmr_cluster_name:
    description: The name of the DMR cluster. Maps to 'dmrClusterName' in the API.
    required: true
    type: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
seealso:
- module: solace.pubsub_plus.solace_dmr_cluster
- module: solace.pubsub_plus.solace_dmr_cluster_cert_matching_rule
- module: solace.pubsub_plus.solace_get_dmr_cluster_cert_matching_rule_conditions
author:
  - Paulus Gunadi (@pjgunadi)
'''

EXAMPLES = '''
hosts: all
gather_facts: no
any_errors_fatal: true
collections:
- solace.pubsub_plus
module_defaults:
  solace_dmr_cluster_cert_matching_rule_condition:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
tasks:
  - name: remove
    solace_dmr_cluster_cert_matching_rule_condition:
      source: san
      expression: "*.example.com"
      cert_matching_rule_name: my-rule
      dmr_cluster_name: foo
      state: absent

  - name: add
    solace_dmr_cluster_cert_matching_rule_condition:
      source: san
      expression: "*.example.com"
      cert_matching_rule_name: my-rule
      dmr_cluster_name: foo
      state: present
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
    returned: success
msg:
    description: The response from the HTTP call in case of error.
    type: dict
    returned: error
rc:
    description: Return code. rc=0 on success, rc=1 on error.
    type: int
    returned: always
    sample:
        success:
            rc: 0
        error:
            rc: 1
'''

from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys  # pylint: disable=unused-import
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceDmrClusterCertMatchingRuleConditionTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'source'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['dmr_cluster_name'], params['cert_matching_rule_name'], params['source'], params['expression']]

    def get_func(self, dmr_cluster_name, cert_matching_rule_name, source, expression):
        # GET /dmrClusters/{dmrClusterName}/certMatchingRules/{certMatchingRuleName}/conditions/{source},{expression}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'dmrClusters', dmr_cluster_name,
                      'certMatchingRules', cert_matching_rule_name, 'conditions', f"{source},{expression}"]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, dmr_cluster_name, cert_matching_rule_name, source, expression, settings=None):
        # POST /dmrClusters/{dmrClusterName}/certMatchingRules/{certMatchingRuleName}/conditions
        data = {
            'dmrClusterName': dmr_cluster_name,
            'certMatchingRuleName': cert_matching_rule_name,
            self.OBJECT_KEY: source,
            'expression': expression
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'dmrClusters', dmr_cluster_name,
                      'certMatchingRules', cert_matching_rule_name, 'conditions']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, dmr_cluster_name, cert_matching_rule_name, source, expression):
        # DELETE /dmrClusters/{dmrClusterName}/certMatchingRules/{certMatchingRuleName}/conditions/{source},{expression}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'dmrClusters', dmr_cluster_name,
                      'certMatchingRules', cert_matching_rule_name, 'conditions', f"{source},{expression}"]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        source=dict(type='str', required=True),
        expression=dict(type='str', required=True),
        cert_matching_rule_name=dict(type='str', required=True),
        dmr_cluster_name=dict(type='str', required=True)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceDmrClusterCertMatchingRuleConditionTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
