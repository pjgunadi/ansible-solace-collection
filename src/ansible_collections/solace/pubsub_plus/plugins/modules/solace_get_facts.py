#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_get_facts
short_description: get facts for a broker/vpn

TODO: copy a sample for solace cloud AND self-hosted

description:
- Provides convenience functions to access solace facts retrieved from broker service using M(solace_gather_facts) from 'ansible_facts.solace'.
notes:
- In order to access other hosts' facts (other than the current 'inventory_host'), you must not use the 'serial' strategy for the playbook.
options:
  hostvars:
    description:
    - "The playbook's 'hostvars'. Contains all facts for all hosts / brokers."
    - "Always set to: 'hostvars: \\"{{ hostvars }}\\""
    required: True
    type: dict
  hostvars_inventory_hostname:
    description: The 'inventory_hostname', i.e. the playbook's host, to retrieve the facts from as available in 'hostvars'.
    required: True
    type: str
  msg_vpn:
    description:
    - The message vpn of the broker to retrieve the facts from.
    - Only required for certain 'get_functions' if more than 1 Vpn exists.
    - Can be omitted if only 1 Vpn exists.
    required: False
    type: str
  get_functions:
    description: List of pre-built functions that retrieve data for the 'hostvars_inventory_hostname'/'msg_vpn' data in 'hostvars'.
    required: False
    type: list
    default: []
    elements: str
    suboptions:
        get_vpnClientConnectionDetails:
            description:
            - Retrieve all enabled client connection details for the various protocols for the service/broker.
            - Requires 'msg_vpn' parameter if more than 1 Vpn exists.
            type: str
            required: no
        get_vpnBridgeRemoteMsgVpnLocations:
            description:
            - "Retrieve enabled remote message vpn locations (plain, secured, compressed) for the service/broker."
            - Requires 'msg_vpn' parameter if more than 1 Vpn exists.
            - "For Solace Cloud: {hostname}:{port}."
            - "For broker: v:{virtualRouterName}."
            type: str
            required: no
        get_vpnAttributes:
            description:
            - Retrieve attributes of the message Vpn.
            - Requires 'msg_vpn' parameter if more than 1 Vpn exists.
            type: str
            required: no
        get_serviceTrustStoreDetails:
            description: Retrieve the URI for to download client certificates if enabled.
            type: str
            required: no
        get_serviceVirtualRouterName:
            description: Retrieve the virtual router name.
            type: str
            required: no
        get_serviceDmrClusterConnectionDetails:
            description:
            - Retrieve DMR cluster connection details for the service/broker.
            - "Note: Currently only supports Solace Cloud services."
            type: str
            required: no
seealso:
- module: solace_gather_facts
- module: solace_cloud_get_facts
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
  solace_gather_facts:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN if broker_type=='solace_cloud' else omit }}"
    solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
tasks:
- name: Gather Solace Facts
  solace_gather_facts:

- name: get_vpnClientConnectionDetails
  solace_get_facts:
    hostvars: "{{ hostvars }}" # always use this setting
    hostvars_inventory_hostname: "{{ inventory_hostname }}"
    msg_vpn: "{{ vpn }}"
    get_functions:
      - get_vpnClientConnectionDetails
  register: result

- name: save to yaml file
  copy:
    content: "{{ result.facts | to_nice_yaml }}"
    dest: "./vpnClientConnectionDetails.yml"
  delegate_to: localhost

- name: print
  debug:
    msg:
      - "result.facts="
      - "{{ result.facts }}"

- name: get other facts
  solace_get_facts:
    hostvars: "{{ hostvars }}"
    hostvars_inventory_hostname: "{{ inventory_hostname }}"
    msg_vpn: "{{ vpn }}"
    get_functions:
      - get_vpnBridgeRemoteMsgVpnLocations
      - get_vpnAttributes
      - get_serviceTrustStoreDetails
      - get_serviceVirtualRouterName
      - get_serviceDmrClusterConnectionDetails
  register: result

- name: print
  debug:
    msg:
      - "result.facts="
      - "{{ result.facts }}"
'''

RETURN = '''
facts:
    description: The facts requested.
    type: dict
    returned: success
    elements: dict
    sample:
        vpnBridgeRemoteMsgVpnLocations:
            compressed: mr1oqbbo5py0k5.messaging.solace.cloud:55003
            enabled: true
            plain: mr1oqbbo5py0k5.messaging.solace.cloud:55555
            secured: mr1oqbbo5py0k5.messaging.solace.cloud:55443
        serviceDmrClusterConnectionDetails:
            clusterName: cluster-aws-ca-central-1a-1oqbbo5py0k5
            password: a442o651ukpdnrpp4anvpl6s4o
            primaryRouterName: pri-aws-ca-central-1a-1oqbbo5py0k5
            remoteAddress: mr1oqbbo5py0k5.messaging.solace.cloud
        serviceTrustStoreDetails:
            enabled: true
            uri: https://www.websecurity.symantec.com/content/dam/websitesecurity/support/digicert/symantec/root/DigiCert_Global_Root_CA.pem
        serviceVirtualRouterName: pri-aws-ca-central-1a-1oqbbo5py0k5
        vpnAttributes:
            msgVpn: asc_test_120
        vpnClientConnectionDetails:
            AMQP:
                authentication:
                    password: jmqjg4eotp6ae5ul4ci75oogoa
                    username: solace-cloud-client
                compressed:
                    enabled: false
                    uri: null
                    uri_components: null
                enabled: true
                plain:
                    enabled: true
                    uri: amqp://mr1oqbbo5py0k5.messaging.solace.cloud:5672
                    uri_components:
                        host: mr1oqbbo5py0k5.messaging.solace.cloud
                        port: 5672
                        protocol: amqp
                secured:
                    enabled: true
                    uri: amqps://mr1oqbbo5py0k5.messaging.solace.cloud:5671
                    uri_components:
                        host: mr1oqbbo5py0k5.messaging.solace.cloud
                        port: 5671
                        protocol: amqps
                ws_plain: null
                ws_secured: null
            JMS:
                authentication:
                    password: jmqjg4eotp6ae5ul4ci75oogoa
                    username: solace-cloud-client
                compressed:
                    enabled: false
                    uri: null
                    uri_components: null
                enabled: true
                plain:
                    enabled: true
                    uri: smf://mr1oqbbo5py0k5.messaging.solace.cloud:55555
                    uri_components:
                        host: mr1oqbbo5py0k5.messaging.solace.cloud
                        port: 55555
                        protocol: smf
                secured:
                    enabled: true
                    uri: smfs://mr1oqbbo5py0k5.messaging.solace.cloud:55443
                    uri_components:
                        host: mr1oqbbo5py0k5.messaging.solace.cloud
                        port: 55443
                        protocol: smfs
                ws_plain: null
                ws_secured: null
            MQTT:
                authentication:
                    password: jmqjg4eotp6ae5ul4ci75oogoa
                    username: solace-cloud-client
                compressed:
                    enabled: false
                    uri: null
                    uri_components: null
                enabled: true
                plain:
                    enabled: true
                    uri: tcp://mr1oqbbo5py0k5.messaging.solace.cloud:1883
                    uri_components:
                        host: mr1oqbbo5py0k5.messaging.solace.cloud
                        port: 1883
                        protocol: tcp
                secured:
                    enabled: true
                    uri: ssl://mr1oqbbo5py0k5.messaging.solace.cloud:8883
                    uri_components:
                        host: mr1oqbbo5py0k5.messaging.solace.cloud
                        port: 8883
                        protocol: ssl
                ws_plain: null
                ws_secured: null
            REST:
                authentication:
                    password: jmqjg4eotp6ae5ul4ci75oogoa
                    username: solace-cloud-client
                compressed:
                    enabled: false
                    uri: null
                    uri_components: null
                enabled: true
                plain:
                    enabled: true
                    uri: http://mr1oqbbo5py0k5.messaging.solace.cloud:9000
                    uri_components:
                        host: mr1oqbbo5py0k5.messaging.solace.cloud
                        port: 9000
                        protocol: http
                secured:
                    enabled: true
                    uri: https://mr1oqbbo5py0k5.messaging.solace.cloud:9443
                    uri_components:
                        host: mr1oqbbo5py0k5.messaging.solace.cloud
                        port: 9443
                        protocol: https
                ws_plain: null
                ws_secured: null
            SMF:
                authentication:
                    password: jmqjg4eotp6ae5ul4ci75oogoa
                    username: solace-cloud-client
                compressed:
                    enabled: true
                    uri: tcp://mr1oqbbo5py0k5.messaging.solace.cloud:55003
                    uri_components:
                        host: mr1oqbbo5py0k5.messaging.solace.cloud
                        port: 55003
                        protocol: tcp
                enabled: true
                plain:
                    enabled: true
                    uri: tcp://mr1oqbbo5py0k5.messaging.solace.cloud:55555
                    uri_components:
                        host: mr1oqbbo5py0k5.messaging.solace.cloud
                        port: 55555
                        protocol: tcp
                secured:
                    enabled: true
                    uri: tcps://mr1oqbbo5py0k5.messaging.solace.cloud:55443
                    uri_components:
                        host: mr1oqbbo5py0k5.messaging.solace.cloud
                        port: 55443
                        protocol: tcps
                ws_plain: null
                ws_secured: null
            brokerMgmtType: solace_cloud
            msgVpn: asc_test_120
            trustStore:
                enabled: true
                uri: https://www.websecurity.symantec.com/content/dam/websitesecurity/support/digicert/symantec/root/DigiCert_Global_Root_CA.pem
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

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceReadFactsTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_facts import SolaceBrokerFacts, SolaceCloudBrokerFacts, SolaceSelfHostedBrokerFacts
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceParamsValidationError, SolaceInternalError
from ansible.module_utils.basic import AnsibleModule


class SolaceGetFactsTask(SolaceReadFactsTask):

    GET_FUNCTIONS = [
        "get_vpnClientConnectionDetails",
        "get_vpnAttributes",
        "get_vpnBridgeRemoteMsgVpnLocations",
        "get_serviceTrustStoreDetails",
        "get_serviceVirtualRouterName",
        "get_serviceDmrClusterConnectionDetails"
    ]
    REQUIRES_VPN = [
        "get_vpnClientConnectionDetails",
        "get_vpnAttributes",
        "get_vpnBridgeRemoteMsgVpnLocations"
    ]

    def __init__(self, module):
        super().__init__(module)
        self.vpn_name = None

    def validate_params(self):
        params = self.get_module().params
        hostvars = params['hostvars']
        hostvars_inventory_hostname = params['hostvars_inventory_hostname']
        param_get_functions = params['get_functions']
        # check hostvars
        if hostvars_inventory_hostname not in hostvars:
            raise SolaceParamsValidationError("hostvars, hostvars_inventory_hostname", hostvars_inventory_hostname, f"cannot find host={hostvars_inventory_hostname} in hostvars - cross check spelling with inventory file")
        if 'ansible_facts' not in hostvars[hostvars_inventory_hostname]:
            raise SolaceParamsValidationError(f"hostvars[{hostvars_inventory_hostname}]", hostvars[hostvars_inventory_hostname], "cannot find 'ansible_facts'")
        if 'solace' not in hostvars[hostvars_inventory_hostname]['ansible_facts']:
            raise SolaceParamsValidationError(f"hostvars[{hostvars_inventory_hostname}]['ansible_facts']", hostvars[hostvars_inventory_hostname]['ansible_facts'], "cannot find 'solace'")
        # get funcs
        has_get_funcs = self.validate_param_get_functions(self.GET_FUNCTIONS, param_get_functions)
        if not has_get_funcs:
            raise SolaceParamsValidationError("get_functions", param_get_functions, "empty. specify at least one")
        # check vpn exists
        search_dict = hostvars[hostvars_inventory_hostname]['ansible_facts']['solace']
        vpns = self.get_vpns(search_dict)
        vpn_name = params['msg_vpn']
        if not vpn_name and len(vpns) == 1:
            vpn_name = vpns[0]
        # check for wrong vpn
        if vpn_name and vpn_name not in vpns:
            raise SolaceParamsValidationError("msg_vpn", params['msg_vpn'], f"vpn does not exist - select one of {vpns}")
        self.vpn_name = vpn_name
        get_functions = params['get_functions']
        if get_functions and len(get_functions) > 0:
            for get_func in get_functions:
                if get_func in self.REQUIRES_VPN and not self.vpn_name:
                    raise SolaceParamsValidationError("msg_vpn", params['msg_vpn'], f"required for get_function={get_func}. vpns found: {vpns}")

    def do_task(self):
        self.validate_params()
        params = self.get_module().params
        hostvars = params['hostvars']
        hostvars_inventory_hostname = params['hostvars_inventory_hostname']
        search_dict = hostvars[hostvars_inventory_hostname]['ansible_facts']['solace']
        get_functions = params['get_functions']
        facts = dict()

        if search_dict['isSolaceCloud']:
            solaceBrokerFacts = SolaceCloudBrokerFacts(search_dict, self.vpn_name)
        else:
            solaceBrokerFacts = SolaceSelfHostedBrokerFacts(search_dict, self.vpn_name)

        if get_functions and len(get_functions) > 0:
            for get_func in get_functions:
                field, value = self.call_dynamic_func(get_func, solaceBrokerFacts)
                facts[field] = value

        result = self.create_result(rc=0, changed=False)
        result['facts'] = facts
        return None, result

    def get_vpns(self, search_dict: dict) -> list:
        return list(search_dict['vpns'].keys())

    def get_vpnClientConnectionDetails(self, solace_broker_facts: SolaceBrokerFacts):
        return 'vpnClientConnectionDetails', solace_broker_facts.get_all_client_connection_details()

    def get_vpnAttributes(self, solace_broker_facts: SolaceBrokerFacts):
        return 'vpnAttributes', solace_broker_facts.get_msg_vpn_attributes()

    def get_vpnBridgeRemoteMsgVpnLocations(self, solace_broker_facts: SolaceBrokerFacts):
        return 'vpnBridgeRemoteMsgVpnLocations', solace_broker_facts.get_bridge_remote_msg_vpn_locations()

    def get_serviceTrustStoreDetails(self, solace_broker_facts: SolaceBrokerFacts):
        return 'serviceTrustStoreDetails', solace_broker_facts.get_trust_store_details()

    def get_serviceVirtualRouterName(self, solace_broker_facts: SolaceBrokerFacts):
        return 'serviceVirtualRouterName', solace_broker_facts.get_virtual_router_name()

    def get_serviceDmrClusterConnectionDetails(self, solace_broker_facts: SolaceBrokerFacts):
        return 'serviceDmrClusterConnectionDetails', solace_broker_facts.get_dmr_cluster_connection_details()


def run_module():
    module_args = dict(
        hostvars=dict(type='dict', required=True),
        hostvars_inventory_hostname=dict(type='str', required=True),
        get_functions=dict(type='list', required=False, default=[], elements='str'),
        msg_vpn=dict(type='str', required=False)
    )
    arg_spec = dict()
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceGetFactsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
