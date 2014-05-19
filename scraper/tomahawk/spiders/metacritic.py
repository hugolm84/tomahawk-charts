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
from scrapy.log import log
from tomahawkspider import TomahawkCrawlSpider
from tomahawk.helpers.tomahawkspiderhelper import extract, TomahawkSpiderHelper
from tomahawk.itemloaders import TomahawkItemLoader


class MetacriticSpider(TomahawkCrawlSpider):

    name = 'Metacritic'

    start_urls = [
        "http://www.metacritic.com/music"
    ]

    genre_nav_xpath = './/ul[@class="genre_nav"]/li'
    next_page_xpath = './/div[@class="page_flipper"]/span[@class="flipper next"]/a'

    current_page_name_xpath = './/ul[contains(@class, "tabs")]/li/span[@class="active"]/span/text()'
    list_xpath = './/ol[contains(@class,"list_product_condensed")]/li'

    rules = (
        TomahawkCrawlSpider.follow_link_as_chart(
            xpath=genre_nav_xpath,
            deny=["music", "name"],
        ),
        TomahawkCrawlSpider.follow_link_as_next(
            xpath=next_page_xpath,
            allow=[r'\?page=[1-2]']
        ),
    )

    def get_current_genre(self, selector):
        navList = selector.xpath(self.genre_nav_xpath)
        for index, item in enumerate(navList):
            if item.xpath('.//span'):
                return item.xpath('.//span/text()').extract()[0].strip()
        return None

    def do_create_chart(self, chart, response):
        name = self.get_current_genre(chart.selector)
        chart.add_value("id", name)
        chart.add_value("name", name)
        chart.add_value("type", TomahawkSpiderHelper.AlbumType)
        chart.add_xpath("description", self.current_page_name_xpath)
        return chart

    def do_parse(self, chart, response):
        selector = Selector(response)

        for rank, item in enumerate(selector.xpath(self.list_xpath)):
            entry = TomahawkItemLoader(selector=item)
            entry.add_value("rank", rank)
            entry.add_xpath("artist", './/span[@class="data"]/text()')
            entry.add_xpath("album", './/a/text()')
            chart.add_value("list", entry.load_item())

        # process the item if there is no more next_pages, otherwise, return none and keep parsing
        next_selector = selector.xpath(self.next_page_xpath)
        if not next_selector:
            self.log("No more next page! Processing")
            return self.do_process_item(chart)

        next_page = extract(self.next_page_xpath+"/@href", selector)[-1:]
        if next_page and int(next_page) > 2:
            self.log("Maximum depth! Processing")
            return self.do_process_item(chart)

        return None