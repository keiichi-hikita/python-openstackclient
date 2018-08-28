# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import copy
import six
from osc_lib.command import command
from osc_lib import utils
from openstackclient.i18n import _  # noqa


def _convert_list_and_setattr(data, attr_name, ip_address_list):
    attr = "\n".join(ip_address_list)
    setattr(data, attr_name, attr)


class ListFirewallConfiguration(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ListFirewallConfiguration, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.sdk.conn.micro_internet_gateway

        columns = [
            'ID',
            'Priority',
            'Direction',
            'Source IP',
            'Destination IP',
            'Application Filter',
            'Protocol Port',
            'Enabled',
        ]
        column_headers = copy.deepcopy(columns)

        data = client.firewall_configurations()

        for datum in data:
            c_source_ip = copy.deepcopy(datum.source_ip)
            c_destination_ip = copy.deepcopy(datum.destination_ip)
            c_protocol_port = copy.deepcopy(datum.protocol_port)

            _convert_list_and_setattr(datum, 'source_ip', c_source_ip)
            _convert_list_and_setattr(datum, 'destination_ip', 
                                      c_destination_ip)
            _convert_list_and_setattr(datum, 'protocol_port', c_protocol_port)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowFirewallConfiguration(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowFirewallConfiguration, self).\
            get_parser(prog_name)
        parser.add_argument(
            'firewall_configuration_id',
            metavar='<firewall-configuration-id>',
            help='ID of firewall configuration to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.sdk.conn.micro_internet_gateway

        rows = [
            'ID',
            'Description',
            'Priority',
            'Direction',
            'Source IP',
            'Destination IP',
            'Application Filter',
            'Protocol Port',
            'Log',
            'IDS IPS',
            'Anti Virus',
            'Anti Spyware',
            'URL Filtering',
            'Enabled',
        ]
        row_headers = rows

        data = client.get_firewall_configuration(
            parsed_args.firewall_configuration_id)

        c_source_ip = copy.deepcopy(data.source_ip)
        c_destination_ip = copy.deepcopy(data.destination_ip)
        c_protocol_port = copy.deepcopy(data.protocol_port)

        _convert_list_and_setattr(data, 'source_ip', c_source_ip)
        _convert_list_and_setattr(data, 'destination_ip', c_destination_ip)
        _convert_list_and_setattr(data, 'protocol_port', c_protocol_port)

        # licenses = data.licenses
        # licenses_json = json.dumps(licenses, indent=2)
        # setattr(data, 'licenses', licenses_json)

        return (row_headers, (utils.get_item_properties(data, rows)))
