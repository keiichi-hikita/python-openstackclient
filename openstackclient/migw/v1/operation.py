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


class ListOperation(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ListOperation, self).get_parser(prog_name)
        parser.add_argument(
            '--resource_id',
            metavar='<resource uuid>',
            help='Resource ID to query operations [Type: String]')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.virtual_network_appliance

        columns = [
            'ID',
            'Resource ID',
            'Request Type',
            'Reception Datetime',
            'Commit Datetime',
            'Status',
        ]
        column_headers = copy.deepcopy(columns)

        data = client.operations()

        resource_id = getattr(parsed_args, 'resource_id', None)
        if resource_id:
            data = [datum for datum in data
                    if datum.resource_id == resource_id]

        sorted(data,
               key=lambda datum: datum.reception_datetime,
               reverse=True)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowOperation(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowOperation, self).\
            get_parser(prog_name)
        parser.add_argument(
            'operation_id',
            metavar='<operation-id>',
            help='ID of operation id to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.virtual_network_appliance

        rows = [
            'ID',
            'Resource ID',
            'Request Type',
            'Status',
            'Reception Datetime',
            'Commit Datetime',
            'Request Body',
            'Warning',
            'Error',
            # 'Error Details',
            'Tenant ID',
            'Resource Type',
        ]
        row_headers = rows

        data = client.get_operation(parsed_args.operation_id)

        if data.request_body:
            req_body = data.request_body
            req_body_dict = json.loads(req_body)
            setattr(data, 'request_body', json.dumps(req_body_dict, indent=2))

        return (row_headers, (utils.get_item_properties(data, rows)))
