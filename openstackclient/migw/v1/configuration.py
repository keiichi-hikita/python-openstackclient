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
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _  # noqa


def _set_configurations(data):
    conf = data.configurations

    result = []
    for k, v in conf.items():
        result.append("{0}: {1}".format(k, v))

    result_str = '\n'.join(result)
    return setattr(data, 'configurations', result_str)


class ConfigurationsBase(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ConfigurationsBase, self).\
            get_parser(prog_name)
        parser.add_argument(
            'cell',
            metavar='<cell-id>',
            help=_('Cell ID to get firewall configurations'),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.sdk.conn.micro_internet_gateway

        rows = [
            'Cell ID',
            'Configurations'
        ]
        row_headers = rows

        query = {'cell_id': parsed_args.cell, 'type': self.config_type}
        data = client.configurations(**query)

        _set_configurations(data)
        return (row_headers, (utils.get_item_properties(data, rows)))


class FirewallConfigurations(ConfigurationsBase):
    config_type = 'firewall'


class GslbConfigurations(ConfigurationsBase):
    config_type = 'gslb'


# class StopVirtualNetworkAppliance(command.Command):
#
#     def get_parser(self, prog_name):
#         parser = super(StopVirtualNetworkAppliance, self).\
#             get_parser(prog_name)
#         parser.add_argument(
#             'virtual_network_appliance',
#             metavar='<virtual-network-appliance-id>',
#             nargs="+",
#             help=_('Virtual Network Appliance(s) to stop'),
#         )
#         return parser
#
#     def take_action(self, parsed_args):
#         vnf_client = self.app.sdk.conn.virtual_network_appliance
#
#         for virtual_network_appliance in parsed_args.virtual_network_appliance:
#             vnf_client.\
#                 stop_virtual_network_appliance(virtual_network_appliance)
#
#
# class RestartVirtualNetworkAppliance(command.Command):
#
#     def get_parser(self, prog_name):
#         parser = super(RestartVirtualNetworkAppliance, self).\
#             get_parser(prog_name)
#         parser.add_argument(
#             'virtual_network_appliance',
#             metavar='<virtual-network-appliance-id>',
#             nargs="+",
#             help=_('Virtual Network Appliance(s) to restart'),
#         )
#         return parser
#
#     def take_action(self, parsed_args):
#         vnf_client = self.app.sdk.conn.virtual_network_appliance
#
#         for virtual_network_appliance in parsed_args.virtual_network_appliance:
#             vnf_client.\
#                 restart_virtual_network_appliance(virtual_network_appliance)
#
#
# class ResetPasswordVirtualNetworkAppliance(command.ShowOne):
#
#     def get_parser(self, prog_name):
#         parser = super(ResetPasswordVirtualNetworkAppliance, self).\
#             get_parser(prog_name)
#         parser.add_argument(
#             'virtual_network_appliance',
#             metavar='<virtual-network-appliance-id>',
#             # nargs="+",
#             help=_('Virtual Network Appliance ID to restart'),
#         )
#         return parser
#
#     def take_action(self, parsed_args):
#         vnf_client = self.app.eclsdk.conn.virtual_network_appliance
#
#         rows = [
#             'ID',
#             'Name',
#             'Username',
#             'New Password'
#         ]
#         row_headers = rows
#
#         vna = parsed_args.virtual_network_appliance
#         data = vnf_client.reset_password_virtual_network_appliance(vna)
#         return (row_headers, utils.get_item_properties(data, rows))


# class ShowVirtualNetworkApplianceConsole(command.ShowOne):
#
#     def get_parser(self, prog_name):
#         parser = super(ShowVirtualNetworkApplianceConsole, self).\
#             get_parser(prog_name)
#         parser.add_argument(
#             'virtual_network_appliance',
#             metavar='<virtual-network-appliance-id>',
#             help=_('Virtual Network Appliance ID to show console url'),
#         )
#         type_group = parser.add_mutually_exclusive_group()
#         type_group.add_argument(
#             '--novnc',
#             dest='url_type',
#             action='store_const',
#             const='novnc',
#             default='novnc',
#             help='Show noVNC console URL (default)',
#         )
#         type_group.add_argument(
#             '--xvpvnc',
#             dest='url_type',
#             action='store_const',
#             const='xvpvnc',
#             help='Show xpvnc console URL',
#         )
#         return parser
#
#     def take_action(self, parsed_args):
#         vnf_client = self.app.eclsdk.conn.virtual_network_appliance
#         vna = parsed_args.virtual_network_appliance
#         data = vnf_client.get_virtual_network_appliance_console(
#             vna, parsed_args.url_type)
#
#         return zip(*sorted(six.iteritems(data)))


def _set_interfaces_for_display(data):
    ifs = data.interfaces
    interfaces_json = json.dumps(ifs, indent=2)
    setattr(data, 'interfaces', interfaces_json)


def _set_interface_names_for_display(data):
    ifs = {}
    for if_key, if_obj in data.interfaces.items():
        ifs[if_key] = {'name': if_obj['name']}
    setattr(data, 'interface_names', json.dumps(ifs, indent=2))
