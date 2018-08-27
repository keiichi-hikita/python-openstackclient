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

from openstackclient.i18n import _  # noqa

from osc_lib.command import command
from osc_lib import utils


class ListFirewallPolicyType(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ListFirewallPolicyType, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.sdk.conn.micro_internet_gateway

        columns = [
            'ID',
            'Name'
        ]
        column_headers = copy.deepcopy(columns)

        data = client.sizes()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))
