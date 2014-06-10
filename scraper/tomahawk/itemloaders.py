#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) Hugo Lindström <hugolm84@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, MapCompose
from scrapy.exceptions import ContractFail

from .processors import DateTime, PassThrough, ListValidator, Slugify
from .items import TomahawkChartItem, TomahawkItem
from .item_utils import strip
from .helpers.tomahawkspiderhelper import TomahawkSpiderHelper


class TomahawkChartLoader(ItemLoader):

    default_item_class = TomahawkChartItem
    default_output_processor = TakeFirst()

    id_in = Slugify()
    parse_start_date_in, parse_end_date_in = (DateTime(),)*2
    list_out = PassThrough()

    def load_item(self):
        if not self._values['id']:
            self.add_value('id', self._values['name'])

        item = self.item
        required_missing_fields = set(item.fields.keys()) - set(self._values.keys())

        if len(required_missing_fields) != 0:
            raise ContractFail("Item %s is missing required fields %s!" % (item.__class__, required_missing_fields))

        self.list_out = ListValidator(TomahawkSpiderHelper.get_item_reqs(self.get_output_value("type")))

        for field_name in self._values:
            out_put = self.get_output_value(field_name)
            if out_put is not None:
                item[field_name] = out_put
            else:
                raise ContractFail("Item %s is missing value for field %s!" % (item.__class__, field_name))
        return item


class TomahawkItemLoader(ItemLoader):

    default_item_class = TomahawkItem
    default_input_processor = MapCompose(strip)
    default_output_processor = TakeFirst()
