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

import copy
import json

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _  # noqa


ROWS_FOR_SHOW = [
    'ID',
    'Name',
    'Description',
    'Availability Zone',
    'Size',
    'Utilization',
    'Status',
    'Interfaces',
]


class ListCell(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ListCell, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.sdk.conn.micro_internet_gateway

        columns = [
            'ID',
            'Name',
            'Region',
            'Size',
            'Firewall Policy Type',
            'Utilization',
            'Status',
        ]
        column_headers = copy.deepcopy(columns)

        data = client.cells()
        sizes = client.sizes()
        regions = client.regions()
        firewall_policy_types = client.firewall_policy_types()

        for datum in data:
            for size in sizes:
                if datum.size_id == size.id:
                    setattr(datum, 'size', size.name)
                    break

        for datum in data:
            for region in regions:
                if datum.region_id == region.id:
                    setattr(datum, 'region', region.name)
                    break

        for datum in data:
            for fwp in firewall_policy_types:
                if datum.firewall_policy_type_id == fwp.id:
                    setattr(datum, 'firewall_policy_type', fwp.name)
                    break

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowCell(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowCell, self).get_parser(prog_name)
        parser.add_argument(
            'cell_id',
            metavar='<cell-id>',
            help='ID of cell id to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.sdk.conn.micro_internet_gateway

        rows = ROWS_FOR_SHOW
        row_headers = rows

        data = client.get_cell(parsed_args.cell_id)

        # Set plan name
        size = client.get_size(data.size_id)
        setattr(data, 'size', size.name)

        # TODO interface information
        _set_interfaces_for_display(data)

        return (row_headers, (utils.get_item_properties(data, rows)))


class CreateCell(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(CreateCell, self).\
            get_parser(prog_name)
        parser.add_argument(
            'size_id',
            metavar='<size-id>',
            help='ID of size')

        parser.add_argument(
            '--interface',
            metavar="<net-id=net-uuid,ip-address=ip-addr,name=interface-name>",
            action='append',
            default=[],
            help=_("Specify interface parameter for "
                   "micro internet gateway. "
                   "You can specify only one interface in creation of "
                   "micro internet gateway. "
                   "net-id: attach interface to network with this UUID, "
                   "ip-address: IPv4 fixed address for interface. "
                   "(You can specify only one address in creation), "
                   "name: Name of Interface (optional)."),
        )

        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of micro internet gateway'),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of micro internet gateway'),
        )

        parser.add_argument(
            '--availability-zone',
            metavar='<availability-zone>',
            help=_('Availability zone that micro internet gateway '
                   'will be created'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.sdk.conn.micro_internet_gateway

        rows = [
            'ID',
            'Name',
            'Description',
            'Size ID',
            'Status',
            # 'Username',
            # 'Password',
        ]
        row_headers = rows

        if len(parsed_args.interface) == 0:
            msg = _("You must specify at least one interface.")
            raise exceptions.CommandError(msg)

        if len(parsed_args.interface) > 1:
            msg = _("You can specify only one interface in micro internet "
                    "gateway creation.")
            raise exceptions.CommandError(msg)

        interfaces = []
        for if_str in parsed_args.interface:
            if_info = {"net-id": "", "ip-address": "",
                       "name": ""}
            if_info.update(utils.parse_vna_interface(if_str))
            if not bool(if_info["net-id"]) or not bool(if_info["ip-address"]):
                msg = _("You must specify network uuid and ip address both")
                raise exceptions.CommandError(msg)

            interfaces.append(if_info)

        interface_object = {}
        if_num = 1
        for interface in interfaces:

            if_key = 'interface_' + str(if_num)
            tmp = {
                if_key: {
                    'network_id': interface['net-id'],
                    'fixed_ips': [
                        {'ip_address': interface['ip-address']}
                    ]
                }
            }
            if interface['name']:
                tmp[if_key].update({'name': interface['name']})

            interface_object.update(tmp)
            if_num += 1

        size_id = \
            parsed_args.size_id

        name = parsed_args.name
        description = parsed_args.description
        # default_gateway = parsed_args.default_gateway
        zone = parsed_args.availability_zone

        data = client.create_micro_internet_gateway(
            size_id=size_id,
            interfaces=interface_object,
            name=name,
            description=description,
            # default_gateway=default_gateway,
            availability_zone=zone,
        )

        return (row_headers, utils.get_item_properties(data, rows))


class DeleteCell(command.Command):

    def get_parser(self, prog_name):
        parser = super(DeleteCell, self).\
            get_parser(prog_name)
        parser.add_argument(
            "cell_id",
            nargs="+",
            help="IDs of cells to be deleted",
            metavar='<cell-id>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.sdk.conn.micro_internet_gateway
        for cell_id in \
                parsed_args.cell_id:
            client.delete_cell(cell_id)


def _set_configurations(data):
    conf = data.configurations

    result = []
    for k, v in conf.items():
        result.append("{0}: {1}".format(k, v))

    result_str = '\n'.join(result)
    return setattr(data, 'configurations', result_str)



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
