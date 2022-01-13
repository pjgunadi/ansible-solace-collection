#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2022, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_get_client_cert_authority_ocsp_trusted_cns
TODO
short_description: get list of rdp rest consumer trusted common names
description:
- "Get a list of Trusted Common Name objects configured on a Rest Delivery Point object's Rest Consumer object."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/restDeliveryPoint/getMsgVpnRestDeliveryPointRestConsumerTlsTrustedCommonNames"
- "Module Sempv2 Monitor: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html#/restDeliveryPoint/getMsgVpnRestDeliveryPointRestConsumerTlsTrustedCommonNames"
options:
  rdp_name:
    description: The name of the Rest Delivery Point. Maps to 'restDeliveryPointName' in the API.
    type: str
    required: true
  rest_consumer_name:
    description: The name of the Rest Delivery Point. Maps to 'restConsumerName' in the API.
    type: str
    required: true
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.get_list
seealso:
- module: solace_rdp_rest_consumer_trusted_cn
author:
- Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
TODO
hosts: all
gather_facts: no
any_errors_fatal: true
collections:
- solace.pubsub_plus
module_defaults:
  solace_get_rdp_rest_consumer_trusted_cns:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
- name: get list config
  solace_get_rdp_rest_consumer_trusted_cns:
    rdp_name: foo
    rest_consumer_name: bar
  register: result

- name: print result
  debug:
    msg:
    - "{{ result.result_list }}"
    - "{{ result.result_list_count }}"

- name: get list monitor
  solace_get_rdp_rest_consumer_trusted_cns:
    api: monitor
    rdp_name: foo
    rest_consumer_name: bar
  register: result

- name: print result
  debug:
    msg:
    - "{{ result.result_list }}"
    - "{{ result.result_list_count }}"
'''

RETURN = '''
result_list:
  description: The list of objects found containing requested fields. Payload depends on API called.
  returned: success
  type: list
  elements: dict
result_list_count:
  description: Number of items in result_list.
  returned: success
  type: int
rc:
  description: Return code. rc=0 on success, rc=1 on error.
  type: int
  returned: always
  sample:
    success:
      rc: 0
    error:
      rc: 1
msg:
  description: The response from the HTTP call in case of error.
  type: dict
  returned: error
'''

from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerGetPagingTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceGetClientCertAuthorityOCSPTrustedCnsTask(SolaceBrokerGetPagingTask):

    MIN_SEMP_V2_VERSION_STR = "2.19"

    def __init__(self, module):
        super().__init__(module)

    def is_supports_paging(self):
        return False

    def get_path_array(self, params: dict) -> list:
        # GET /clientCertAuthorities/{certAuthorityName}/ocspTlsTrustedCommonNames
        return ['clientCertAuthorities', params['client_cert_authority_name'], 'ocspTlsTrustedCommonNames']


def run_module():
    module_args = dict(
        client_cert_authority_name=dict(type='str', required=True)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()

    # maybe not needed? like in client profile
    # arg_spec.update(SolaceTaskBrokerConfig.arg_spec_solace_cloud())
    arg_spec.update(
        SolaceTaskBrokerConfig.arg_spec_get_object_list_config_montor())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceGetClientCertAuthorityOCSPTrustedCnsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
