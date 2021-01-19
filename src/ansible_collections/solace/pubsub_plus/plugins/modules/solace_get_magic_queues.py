#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_get_magic_queues
TODO: rework doc
short_description: get 'magic' queues

description:
- "Get a list of 'magic' Queue Objects that are generated by the Broker, e.g. #mqtt, #rdp, ..."

options:
    where_name:
        description:
        - "Query for queue name. Maps to <name> in the API."
        - "Examples: #mqtt/*, #rdp/* "
        required: true
        type: str
notes:
- Uses SEMP v1.
- "Reference: U(https://docs.solace.com/Configuring-and-Managing/Monitoring-Guaranteed-Messaging.htm#Viewing)."

extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn

author:
  - Ricardo Gomez-Ulmke (@rjgu)
'''

EXAMPLES = '''
hosts: all
gather_facts: no
any_errors_fatal: true
collections:
- solace.pubsub_plus
module_defaults:
  solace_mqtt_session:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
  solace_get_magic_queues:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
  - name: create mqtt session
    solace_mqtt_session:
        name: foo
        state: present

  - name: "Get MQTT Magic Queues"
    solace_get_magic_queues:
        where_name: "#mqtt/*"
    register: result

  - set_fact:
        magic_queues: "{{ result.result_list }}"

  - name: "Check: All magic Queues are ON/ON"
    fail:
        msg: "Magic queue: ingress or egress is 'Down' for magic_queue: {{ magic_queue.name }} "
    when: magic_queue.info['ingress-config-status'] == "Down" or magic_queue.info['egress-config-status'] == "Down"
    loop: "{{ magic_queues }}"
    loop_control:
        loop_var: magic_queue

'''

RETURN = '''
rc:
    description: "return code. on success: rc=0, on failure: rc=1"
    type: int
    returned: always

result_list:
    description: The list of objects found containing requested fields.
    returned: success
    type: list
    elements: dict
    sample:
      - info:
            access-type: exclusive
            bind-count: '0'
            current-spool-usage-in-mb: '0'
            durable: 'true'
            egress-config-status: Down
            egress-selector-present: 'No'
            high-water-mark-in-mb: '0'
            ingress-config-status: Down
            message-vpn: default
            num-messages-spooled: '0'
            topic-subscription-count: '3'
            type: Primary
        name: "#mqtt/ansible_solace_test_mqtt__1__/180"
result_list_count:
    description: Number of items in result_list.
    returned: success
    type: int

'''

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceGetTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV1PagingGetApi
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceGetMagicQueuesTask(SolaceGetTask):

    def __init__(self, module):
        super().__init__(module)
        self.config = SolaceTaskBrokerConfig(module)
        self.sempv1_get_paging_api = SolaceSempV1PagingGetApi(module)

    def get_config(self) -> SolaceTaskBrokerConfig:
        return self.config

    def get_list(self):
        params = self.get_config().get_params()
        request = {
            'rpc': {
                'show': {
                    'queue': {
                        'name': params['where_name'],
                        'vpn-name': params['msg_vpn'],
                        # test: not found
                        # 'name': "does-not-exist",
                        # 'vpn-name': "does-not-exist",
                        # test: paging
                        # 'count': '',
                        # 'num-elements': 1
                    }
                }
            }
        }
        response_list_path_array = ['rpc-reply', 'rpc', 'show', 'queue', 'queues', 'queue']
        return self.sempv1_get_paging_api.get_objects(self.get_config(), request, response_list_path_array)

    def do_task(self):
        objects = self.get_list()
        result = self.create_result_with_list(objects)
        return None, result


def run_module():
    module_args = dict(
        where_name=dict(type='str', required=True)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )
    solace_task = SolaceGetMagicQueuesTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
