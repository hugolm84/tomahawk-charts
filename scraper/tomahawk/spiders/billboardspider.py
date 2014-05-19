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


class BillboardSpider(TomahawkCrawlSpider):

    name = 'Billboard'

    start_urls = [
        'http://www.billboard.com/charts',
    ]

    chart_items_xpath = '//span[@class="field-content"]'
    next_page_xpath = '//li[@class="pager-next last"]'

    rules = (
        TomahawkCrawlSpider.follow_link_as_chart(
            xpath=chart_items_xpath,
            #allow=['/billboard-200$', '/hot-100']
        ),
        TomahawkCrawlSpider.follow_link_as_next(
            xpath=next_page_xpath,
            allow=[r'\?page=[1-9]']
        ),
    )

    # Some types cant be distinguished by the name
    artist_charts = ['social 50', 'uncharted', 'next big sound']
    album_charts = ['soundtracks', 'billboard 200', 'tastemakers']
    track_charts = ['hot 100', 'airplay', 'youtube', 'adult contemporary', 'ringtones']

    def do_create_chart(self, chart, response):
        name = extract('//h1[@id="page-title"]/text()', chart.selector)
        chart.add_value("id", name)
        chart.add_value("name", name)
        chart.add_value("type", self.extract_type(chart))
        chart.add_value("description", 'Description')
        return chart

    def do_parse(self, chart, response):
        selector = Selector(response)
        items_xpath = '//div[@class="listing chart_listing"]/article/header'
        items = selector.xpath(items_xpath)

        item_type = self.do_get_type(chart)

        for item in items:
            entry = TomahawkItemLoader(selector=item)
            entry.add_xpath("rank", './/span/text()')
            entry.add_xpath(item_type, './/h1/text()')

            # Almost all items have a <a> field for artists.
            # First try to extract the text() from the a field, if that doesnt work, try to extract text() from the
            # selector

            artist_selector = item.xpath('.//p[@class="chart_info"]')
            artist = extract('.//a/text()', artist_selector)

            if not artist:
                artist = extract('.//text()', artist_selector)

            entry.add_value("artist", artist)
            chart.add_value("list", entry.load_item())

        # process the item if there is no more next_pages, otherwise, return none and keep parsing
        if not selector.xpath(self.next_page_xpath):
            return self.do_process_item(chart)
        return None
