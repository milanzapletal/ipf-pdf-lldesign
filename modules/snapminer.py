#!/usr/bin/python3
import sys
import requests


class MineSnapshot:
    def __init__(self, server_url, snapshot_id, site_name, api_key, secure_conn):
        self.server_url = server_url
        self.server_api_url = self.server_url + "api/v1"
        self.snapshot_id = snapshot_id
        self.site_name = site_name
        self.api_key = api_key
        self.headers = {'X-API-Token': self.api_key,
                        'Content-Type': 'application/json'}
        self.secure_conn = secure_conn
        self.snapshot_endpoint = '/snapshots'
        self.filter = {'siteName': ['eq', 'L66']}
        self.universal_load = {'pagination': {'limit': 1, 'start': 0},
                               'snapshot': self.snapshot_id, 'columns': ['id'],
                               'filters': self.filter, 'reports': 'x'}

    def __str__(self):
        return f"To mine data from snapshot_id: {self.snapshot_id}"

    def uniget(self, endpoint):
        try:
            get_request = requests.get(
                self.server_api_url + endpoint, headers=self.headers, verify=self.secure_conn)
        except Exception as err:
            print(
                "  ERROR - Exception occured when connecting to:  {}".format(self.server_api_url))
            print("        - {}".format(err))
            sys.exit()
        if not get_request.ok:
            print('  API GET Error - Unable to GET data from endpoint: ', endpoint)
            print('  --Error: ', get_request.text)
        return get_request.json()

    def unipost(self, endpoint, payload):
        post_request = requests.post(
            self.server_api_url + endpoint, headers=self.headers, json=payload, verify=self.secure_conn)
        if not post_request.ok:
            print('  API POST Error - Unable to POST data from endpoint: ', endpoint)
            print('  --Error: ', post_request.text)
            return {'_meta': {'count': 0}}
        return post_request.json()

    def unicount(self, endpoint, payload=False):
        if not payload:
            return self.unipost(endpoint, self.universal_load)['_meta']['count']
        return self.unipost(endpoint, payload)['_meta']['count']

    def datapost(self, endpoint, column):
        post_payload = {'snapshot': self.snapshot_id, 'columns': [
            column], 'filters': self.filter, 'reports': 'x'}
        post_request = requests.post(
            self.server_api_url + endpoint, headers=self.headers, json=post_payload, verify=self.secure_conn)
        if not post_request.ok:
            print('  API POST Error - Unable to POST data from endpoint: ', endpoint)
            print('  --Error: ', post_request.text)
            return []
        return post_request.json()['data']

    def mine_snap_data(self):
        snapshot_data = dict()
        snapshots_list = self.uniget(self.snapshot_endpoint)

        if snapshots_list == 0:
            print('  ERROR - No snapshots found.')
            sys.exit()

        for snap in snapshots_list:
            if snap['id'] == self.snapshot_id and snap['state'] == 'loaded':
                print(
                    '  -- Snapshot ID: {} detected as loaded - extracting data'.format(self.snapshot_id))
                snapshot_data = snap
        if len(snapshot_data) == 0:
            print(
                '  ERROR - Issues with reading the snapshot ID: {}.'.format(self.snapshot_id))
        return snapshot_data

    def mine_base_data(self):
        print('  Getting base data from url: ', self.server_url)
        base_endpoints = {
            'e_hostname': '/os/hostname',
            'e_version': '/os/version',
            'e_devices': '/tables/inventory/devices',
            'e_hosts': '/tables/addressing/hosts',
            'e_interfaces': '/tables/inventory/interfaces',
            'e_switchport': '/tables/interfaces/switchports',
            'e_vlans': '/tables/vlan/network-summary',
            'e_channels': '/tables/interfaces/port-channel/member-status',
            'e_vrf': '/tables/vrf/summary',
            'e_ipsec_tunnels': '/tables/security/ipsec/tunnels',
            'e_ipsec_gateways': '/tables/security/ipsec/gateways',
            'e_wcontrollers': '/tables/wireless/controllers',
            'e_waps': '/tables/wireless/access-points',
            'e_wclients': '/tables/wireless/clients',
            'e_rules': '/reports?snapshot=' + self.snapshot_id,
            }
        route_endpoints = {
            "bgp": '/tables/networks/summary/protocols/bgp',
            "ospf": '/tables/networks/summary/protocols/ospf',
            "ospfv3": '/tables/networks/summary/protocols/ospfv3',
            "isis": '/tables/networks/summary/protocols/isis',
            # "rip" : '/tables/networks/summary/protocols/rip',
            }
        pagination = {'pagination': {'limit': 1, 'start': 0}}
        base_payloads = {
            'l_active_int': {**pagination, "snapshot": self.snapshot_id, "columns": ['l2'], 'reports': 'x', "filters": {**self.filter, "l2": ["like", "up"]}},
            'l_edge_int': {**pagination, "snapshot": self.snapshot_id, "columns": ['edge'], 'reports': 'x', "filters": {**self.filter, "edge": ["eq", "true"]}},
        }

        def get_routing_protocols(endpoints_input):
            output = list()
            for endpoint in endpoints_input:
                r_test = requests.post(
                    self.server_api_url + endpoints_input[endpoint], headers=self.headers, json=self.universal_load, verify=self.secure_conn)
                if (r_test.json()['_meta']['count'] > 0):
                    output.append(endpoint.upper())
            return output
        full_details = {
            'System Hostname': self.uniget(base_endpoints['e_hostname'])['hostname'].split('\n')[0],
            'System Version': self.uniget(base_endpoints['e_version'])['version'],
            'Snapshots available': len(self.uniget(self.snapshot_endpoint)),
            'Snapshot ID:': self.snapshot_id,
            'Site Name:': self.site_name,
            'Number of devices': self.unicount(base_endpoints['e_devices']),
            'Number of hosts': self.unicount(base_endpoints['e_hosts']),
            'Number of interfaces': self.unicount(base_endpoints['e_interfaces']),
            'Number of active ints': self.unicount(base_endpoints['e_interfaces'], base_payloads['l_active_int']),
            'Number of edge ints': self.unicount(base_endpoints['e_switchport'], base_payloads['l_edge_int']),
            'Detected Port-Channels': self.unicount(base_endpoints['e_channels']),
            'Detected unique VLAN IDs': self.unicount(base_endpoints['e_vlans']),
            'Detected unique VRF names': self.unicount(base_endpoints['e_vrf']),
            'Number of IPSec Tunnels': self.unicount(base_endpoints['e_ipsec_tunnels']),
            'Number of IPSec Gateways': self.unicount(base_endpoints['e_ipsec_gateways']),
            'Routing protocols': get_routing_protocols(route_endpoints),
        }
        return full_details

    def mine_management(self):
        mgmt_endpoints = {
            'e_aaa':  '/tables/security/aaa/servers',
            'e_ntp':  '/tables/management/ntp/sources',
            'e_snmp':  '/tables/management/snmp/trap-hosts',
            'e_telnet':  '/tables/security/enabled-telnet',
            'e_syslog':  '/tables/management/logging/remote',
            'e_netflow':  '/tables/management/flow/netflow/collectors',
            'e_sflow':  '/tables/management/flow/sflow/collectors',
            'e_mirror':  '/tables/management/port-mirroring'
        }
        # Following function is a very quick & dirty response to late night hour

        def get_servers(data_endpoint, column):
            total_count, item_json, item_list, item_string = 0, {}, [], ''
            data = self.datapost(data_endpoint, column)
            for item in data:
                total_count += 1
                item_value = item[column]
                if item_value is None:
                    continue
                if item_value in item_json:
                    item_json[item_value] += 1
                else:
                    item_json[item_value] = 1
            for i in item_json:
                i_percent = round(item_json[i] / total_count * 100, 4)
                item_list.append([item_json[i], i, '['+str(i_percent)+'%'+']'])
            for l in sorted(item_list, reverse=True):
                item_string += l[1] + ' - ' + str(l[0]) + ' ' + l[2] + ', '
            return item_string[:-2]
        return {
            'AAA Servers (server - count [share])': get_servers(mgmt_endpoints['e_snmp'], 'dstHost'),
            'NTP Servers (server - count [share])': get_servers(mgmt_endpoints['e_ntp'], 'source'),
            'Syslog Servers (server - count [share])': get_servers(mgmt_endpoints['e_syslog'], 'host'),
            'Netflow Collectors (collector - count [share])': get_servers(mgmt_endpoints['e_netflow'], 'collector'),
            'sFlow Collectors (collector - count [share])': get_servers(mgmt_endpoints['e_sflow'], 'collector'),
            'Telnet enabled devices total': self.unicount(mgmt_endpoints['e_telnet'], self.universal_load)
        }
