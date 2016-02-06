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

    # Realtime charts, Get the JSON at: http://realtime.billboard.com/tracks/?chart=1&chartName=Overall&limit=20&offset=0
    # Note: We do not include these in the charts

    chart_items_xpath = '//span[@class="field-content"]'
    next_page_xpath = '//li[@class="pager-next last"]'

    rules = (
        TomahawkCrawlSpider.follow_link_as_chart(
            xpath=chart_items_xpath,
            deny=['realtime'],
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
        name = extract('//span[@class="how-it-works__title"]/text()', chart.selector)
        chart.add_value("name", name)
        chart.add_value("type", self.extract_type(chart))
        chart.add_value("description", 'Description')
        return chart

    def do_parse(self, chart, response):
        selector = Selector(response)
        items_xpath = '//div[contains(@class,"chart-data")]/div[@class="container"]/article[contains(@class,"chart-row")]'
        items = selector.xpath(items_xpath)

        item_type = self.do_get_type(chart)

        for item in items:
            entry = TomahawkItemLoader(selector=item)
            entry.add_xpath("rank", './/div[@class="chart-row__primary"]/div[@class="chart-row__rank"]/span/text()')

            # H2 is Artist or Song
            entry.add_xpath(item_type, './/div[@class="chart-row__primary"]/div[@class="chart-row__title"]/h2/text()')
            entry.add_xpath(item_type, './/div[@class="track"]/span[@class="track-info"]/span[@class="web-only"]/a/text()')

            if item_type is not 'Artist':
                entry.add_xpath("artist", './/div[@class="chart-row__primary"]/div[@class="chart-row__title"]/h3/text()')
                entry.add_xpath("artist", './/div[@class="chart-row__primary"]/div[@class="chart-row__title"]/h3/a/text()')

            chart.add_value("list", entry.load_item())

        # process the item if there is no more next_pages, otherwise, return none and keep parsing
        if not selector.xpath(self.next_page_xpath):
            return self.do_process_item(chart)
        return None
