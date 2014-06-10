#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) Ben Evans <ben@bensbit.co.uk>
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

import json
from scrapy.http.request import Request
from tomahawkspider import TomahawkCrawlSpider, TomahawkSpiderHelper
from tomahawk.itemloaders import TomahawkItemLoader

class RedditSpider(TomahawkCrawlSpider):

    name = "Reddit"
    baseUrl = "http://rcharts.bensbit.co.uk"
    sections = ["Music", "listentothis", "dubstep", "trance", "treemusic", "IndieFolk", "metal", "electronicmusic",
                "punk", "rap"]
    apiKey = "3f578b3d250b47adb24e193ba933a9b80f31d3f9"

    def start_requests(self):
        for section in self.sections :
            yield Request('{baseUrl}/r/{section}.json'.format(baseUrl=self.baseUrl, section=section),
                          callback=self.__parse_as_chart__,
                          meta={'section': section})

    def do_create_chart(self, chart, response):
        section = response.meta['section'].capitalize()
        chart.add_value("name", section)
        chart.add_value("id", self.name+section)
        chart.add_value("type", TomahawkSpiderHelper.TrackType)
        chart.add_value("description", "Reddit generated music charts for %s" % section)
        return chart

    def do_parse(self, chart, response):
        response = json.loads(response.body_as_unicode())
        for rank, item in enumerate(response['tracks']):
            entry = TomahawkItemLoader()
            entry.add_value("artist", item['artist'])
            entry.add_value("track", item['title'])
            entry.add_value("rank", rank)
            chart.add_value("list", entry.load_item())

        return self.do_process_item(chart)