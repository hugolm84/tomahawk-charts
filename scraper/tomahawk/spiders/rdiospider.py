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
#

from scrapy.http.request import Request
import json
from tomahawkspider import TomahawkCrawlSpider, TomahawkSpiderHelper
from tomahawk.itemloaders import TomahawkItemLoader


class RdioSpider(TomahawkCrawlSpider):

    name = "Rdio"
    base_url = "http://api.rdio.com/1/"
    oauth_key = 'gk8zmyzj5xztt8aj48csaart'
    oauth_consumer_secret = 'yt35kakDyW'

    # Regions, might change http://www.rdio.com/availability/
    regions = [ "US"]#, "SE", "CA", "DE", "GB", "AU",
                #"BE", "BR", "DK", "EE", "FI", "FR",
                #"IS", "IE","IT", "LV", "LT", "NL",
                #"NZ", "NO", "PT", "ES"]
    default_region = "US"
    default_type = "Track"

    base_types = ["Artist", "Album", "Track"]

    def __init__(self, name=None, **kwargs):
        super(RdioSpider, self).__init__()

    def start_requests(self):
        for base_type in self.base_types:
            for region in self.regions:
                yield Request(url=self.base_url, method='POST', dont_filter=True,
                              meta={'oauth_method_args': {'method': 'getTopCharts','type': base_type,'_region': region}},
                              callback=self.__parse_as_chart__)

    def do_create_chart(self, chart, response):
        meta = response.meta['oauth_method_args']
        name = "Top Overall"
        type = meta['type']
        region = meta['_region']
        chart.add_value("name", name)
        chart.add_value("id", name+type+region)
        chart.add_value("type", type)
        chart.add_value("geo", region)
        chart.add_value("description", "%s %s's in %s" % (name, type, region))
        return chart

    def do_parse(self, chart, response):
        response = json.loads(response.body)
        item_type = self.do_get_type(chart)

        for rank, items in enumerate(response['result']):
            entry = TomahawkItemLoader()
            entry.add_value(item_type, items.pop('name'))

            if item_type != TomahawkSpiderHelper.ArtistType.lower():
                entry.add_value("artist",items.pop("artist"))

            entry.add_value("rank", rank)
            chart.add_value("list", entry.load_item())

        return self.do_process_item(chart)
