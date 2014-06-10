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

from scrapy.selector import Selector
from tomahawkspider import TomahawkCrawlSpider
from tomahawk.helpers.tomahawkspiderhelper import extract
from tomahawk.itemloaders import TomahawkItemLoader


class HotNewHiphopSpider(TomahawkCrawlSpider):

    name = 'HotNewHiphop'
    allowed_domains = ["hotnewhiphop.com"]

    list_urls = [
        "http://www.hotnewhiphop.com/top100/",
        "http://www.hotnewhiphop.com/mixtapes/top100/mainstream/today/",
        "http://www.hotnewhiphop.com/top100/best/"
    ]

    boxed_urls = [
        #popular
        "http://www.hotnewhiphop.com/mixtapes/",
        "http://www.hotnewhiphop.com/songs/",
        "http://www.hotnewhiphop.com/artists/",
        #latest
        "http://www.hotnewhiphop.com/songs/popular/mainstream/today/",
        "http://www.hotnewhiphop.com/mixtapes/popular/mainstream/today/",
        ]

    start_urls = list_urls+boxed_urls

    track_charts = ['hall of fame']
    album_charts = ['mixtapes']

    def parse(self, response):
        return self.__parse_as_chart__(response)

    def get_boxed_name(self, selector):
        name = extract('.//h1[contains(@class, "fidel-black title-14")]//text()', selector)
        identifier = extract('.//div[@class="pull-left active-tab tab-item"]//text()', selector)
        return '%s %s' % (identifier, name)

    def get_list_name(self, selector):
        return " ".join(selector.xpath('.//h1[contains(@class, "active-title")]//text()').extract())

    def do_create_chart(self, chart, response):
        selector = Selector(response)

        name = " ".join((self.get_list_name(selector) or self.get_boxed_name(selector)).split()).capitalize()
        name = name.replace("Top 100", "Top 10")

        chart.add_value('name', name)
        chart.add_value("type", self.extract_type(chart))
        chart.add_value("description", "%s in Hiphop" % name)
        return chart

    def do_parse(self, chart, response):
        selector = Selector(response)
        type = self.type_from_name(self.do_get_type(chart))

        if response.url in self.boxed_urls:
            item_selector = selector.xpath('.//*[@class="row"]/li')
        else:
            item_selector = selector.xpath('.//ul[@class="m0"]/li')

        for rank, item in enumerate(item_selector):
            entry = TomahawkItemLoader(selector=item)

            if type is self.ArtistType:
                entry.add_xpath(type.lower(), './/span[@class="list-item-title"]/a/text()')
            else:
                entry.add_xpath(type.lower(), './/em[@class="list-item-name"]/text()')
                entry.add_xpath("artist", './/em[@class="list-item-subname"]/strong/text()')

            entry.add_value("rank", rank)
            chart.add_value("list", entry.load_item())

        return self.do_process_item(chart)
