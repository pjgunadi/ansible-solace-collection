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
module: solace_telemetry_profile_trace_filter_subscriptions
short_description: list of subscriptions on a telemetry profile trace filter
description:
- "Configure a list of Subscription objects on a Telemetry Profile Trace Filter in a single transaction."
- "Allows addition and removal of a list of Subscription objects as well as replacement of all existing objects on a trace filter."
- "Supports 'transactional' behavior with rollback to original list in case of error."
- "De-duplicates the Subscription object list."
- "To delete all Subscription objects, use state='exactly' with an empty/null list (see examples)."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/msgVpn/\
  createMsgVpnTelemetryProfileTraceFilterSubscription"
options:
  names:
    description: The subscription topics. Maps to 'subscription' in the SEMP v2 API.
    required: true
    type: list
    aliases: [topics, subscriptions]
    elements: str
  subscription_syntax:
    description: The syntax of the subscription topics. Maps to 'subscriptionSyntax' in the API.
    required: false
    default: smf
    type: str
    choices: [smf, mqtt]
  trace_filter_name:
    description: The name of the Trace Filter. Maps to 'traceFilterName' in the API.
    required: true
    type: str
  telemetry_profile_name:
    description: The name of the Telemetry Profile. Maps to 'telemetryProfileName' in the API.
    required: true
    type: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state_crud_list
seealso:
- module: solace.pubsub_plus.solace_telemetry_profile_trace_filter
- module: solace.pubsub_plus.solace_telemetry_profile_trace_filter_subscription
- module: solace.pubsub_plus.solace_get_telemetry_profile_trace_filter_subscriptions
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
    solace_telemetry_profile_trace_filter_subscriptions:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
  tasks:
  - name: add list of subscriptions
    solace_telemetry_profile_trace_filter_subscriptions:
      telemetry_profile_name: my-profile
      trace_filter_name: my-filter
      subscription_syntax: smf
      subscriptions:
        - "topic-1/>"
        - "topic-2/>"
      state: present

  - name: replace subscriptions
    solace_telemetry_profile_trace_filter_subscriptions:
      telemetry_profile_name: my-profile
      trace_filter_name: my-filter
      subscriptions:
        - "new-topic/>"
      state: exactly

  - name: delete all subscriptions
    solace_telemetry_profile_trace_filter_subscriptions:
      telemetry_profile_name: my-profile
      trace_filter_name: my-filter
      subscriptions: null
      state: exactly
'''

RETURN = '''
response:
    description: The response of the operation.
    type: dict
    returned: always
    sample:
      success:
        response:
          -   added: "topic-1/>"
          -   deleted: "topic-2/>"
      error:
        response:
          -   error: "invalid-topic"
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTopicExListTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceTelemetryProfileTraceFilterSubscriptionsTask(SolaceBrokerCRUDTopicExListTask):

    OBJECT_KEY = 'subscription'
    TOPIC_SYNTAX_KEY = 'subscriptionSyntax'

    def __init__(self, module):
        super().__init__(module)

    def get_objects_path_array(self) -> list:
        # GET .../telemetryProfiles/{telemetryProfileName}/traceFilters/{traceFilterName}/subscriptions
        params = self.get_config().get_params()
        return ['msgVpns', params['msg_vpn'], 'telemetryProfiles', params['telemetry_profile_name'],
                'traceFilters', params['trace_filter_name'], 'subscriptions']

    def get_objects_result_data_object_keys(self) -> list:
        return [self.TOPIC_SYNTAX_KEY, self.OBJECT_KEY]

    def get_crud_args(self, object_key) -> list:
        params = self.get_module().params
        list = object_key.split(',')
        if len(list) == 2:
            subscription_syntax = list[0]
            subscription = list[1]
        else:
            subscription_syntax = params['subscription_syntax']
            subscription = list[0]
        return [params['msg_vpn'], params['telemetry_profile_name'], params['trace_filter_name'],
                subscription_syntax, subscription]

    def create_func(self, vpn_name, telemetry_profile_name, trace_filter_name, subscription_syntax, subscription, settings=None):
        # POST .../traceFilters/{traceFilterName}/subscriptions
        data = {
            'msgVpnName': vpn_name,
            'telemetryProfileName': telemetry_profile_name,
            'traceFilterName': trace_filter_name,
            self.TOPIC_SYNTAX_KEY: subscription_syntax,
            self.OBJECT_KEY: subscription
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'telemetryProfiles',
                      telemetry_profile_name, 'traceFilters', trace_filter_name, 'subscriptions']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, vpn_name, telemetry_profile_name, trace_filter_name, subscription_syntax, subscription):
        # DELETE .../traceFilters/{traceFilterName}/subscriptions/{subscriptionSyntax},{subscription}
        sub_uri = ','.join([subscription_syntax, subscription])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'telemetryProfiles',
                      telemetry_profile_name, 'traceFilters', trace_filter_name, 'subscriptions', sub_uri]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        telemetry_profile_name=dict(type='str', required=True),
        trace_filter_name=dict(type='str', required=True),
        subscription_syntax=dict(type='str', default='smf', choices=['smf', 'mqtt']),
        names=dict(type='list',
                   required=True,
                   aliases=['topics', 'subscriptions'],
                   elements='str'
                   ),
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud_list())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceTelemetryProfileTraceFilterSubscriptionsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
