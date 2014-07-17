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

'''
from tomahawkspider import TomahawkCrawlSpider
from tomahawk.itemloaders import TomahawkItemLoader
from scrapy.selector import Selector

class ExampleSpider(TomahawkCrawlSpider):

    # Required: name
    name = "Example"

    # Semi-Required: start_urls can be populated via the __init__ function of your spider
    start_urls = [
        "http://www.billboard.com/charts",
        ]

    # Optional: Allowed domains limits the scope when the spider "crawls" away from the start_urls
    allowed_domains = [
        "billboard.com"
    ]


    #Rules simply parsing of pages that requires the spider to crawl away from the start_urls.
    #    Using the "follow_link_as_chart" rule, we can tell the spider that each link scraped and followed should be
    #    considered as a new chart. TomahawkCrawlSpider will call the unimplemented "do_create_chart" when the new chart
    #    is initiated, and you can then add values to it based on the response you get.

    #    Using the "follow_link_as_next" we can tell the spider that the link found in the xpath, leads to the next
    #    page of the chart.

    #    Callback: Both rules calls the unimplemented "do_parse" method.

    #    You can easily create custom rules via the "follow_link" method.
    #        rule = TomahawkCrawlSpider.follow_link(xpath, allow_relative_urls, deny_relative_urls, callback, cb_kwags)

    chart_items_xpath   = '//span[@class="field-content"]'
    next_page_xpath     = '//li[@class="pager-next last"]'

    rules = (
        # Follow each link found on the start_pages and treat it as a chart.
        # Only allow certain links
        # Deny /youtube
        TomahawkCrawlSpider.follow_link_as_chart(
            chart_items_xpath,
            allow = ['/hot-100', '/radio-songs', '/social-50'],
            deny = ['/youtube']
        ),
        # Follow each link found on a chart page, but only allow links to pages 1-9
        TomahawkCrawlSpider.follow_link_as_next(
            next_page_xpath,
            allow=[r'\?page=[1-9]']
        ),
    )


    #TomahawkSpiderHelper tries to match some string to a type from the chart name.
    #    Usually a chart is named Top Rap Songs or Reggae Albums, but sometimes we need to specify what is what.
    #    Define those names in self.artist|album|track_charts[] and the helper will map the name to the correct type.

    artist_charts   = ['social 50', 'uncharted']
    album_charts    = ['soundtracks', 'billboard 200', 'tastemakers']
    track_charts    = ['the hot 100']

    #This is a callback from TomahawkCrawlSpider, which gets called when a chart is created.
    #    The CrawlSpider adds some necessary fields, like origin, parse_date and source (self.name) and passes it along
    #    for us to modify.

    def do_create_chart(self, chart, response):
        # Extract the name of the chart from a xpath. In this case, the selector is set to the xpath passed to the rule
        name = extract('//h1[@id="page-title"]/text()', chart.selector)
        # Name: Required
        chart.add_value("name", name)
        # Id: Required
        chart.add_value("id", name)
        # Type: Required
        chart.add_value("type", self.extract_type_from_name(name))
        # Description: Required
        chart.add_value("description", "Some chart description")
        return chart

    #This is a callback from TomahawkCrawlSpider, which gets called when a link was followed as a chart or as a next_page

    def do_parse(self, chart = None, response = None):
        # Create a new xpath selector from the response
        selector = Selector(response)
        # All the items we are concerned of resides in this div class/article/header
        items_xpath = '//div[@class="listing chart_listing"]/article/header'
        # Create xpath numerator
        items = selector.xpath(items_xpath)

        for itemSelector in items:
            # Create a new ItemLoader with the itemSelector
            item = TomahawkItemLoader(selector=itemSelector)
            # Find and add the text() from xpath
            item.add_xpath("rank", './/span/text()')
            # Find and add the text() from xpath
            item.add_xpath("track", './/h1/text()')

            # Not all items have <a> field for artists.
            # First try to extract the text() from the a field, if that doesnt work, try to extract text() from the selector

            artist_selector = itemSelector.xpath('.//p[@class="chart_info"]')
            artist = extract('.//a/text()', artist_selector)
            if not artist:
                artist = extract('.//text()', artist_selector)
            item.add_value("artist", artist)

            chart.add_value("list", item.load_item())

        # If we can find a next_page link, process the item as we consider it done
        if not selector.xpath(self.next_page_xpath):
            return self.do_process_item(chart)
        # We know this chart has more data to be parsed, return None
        return None
'''