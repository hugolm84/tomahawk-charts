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
from tomahawk.itemloaders import TomahawkItemLoader
import json
from scrapy.http.request import Request

class ItunesSpider(TomahawkCrawlSpider):

    name = 'Itunes'

    start_urls = [
        'https://rss.itunes.apple.com/data/lang/en-US/common.json',
        ]

    available_feeds = 'http://itunes.apple.com/WebObjects/MZStoreServices.woa/wa/RSS/wsAvailableFeeds?cc=%s'
    max_items = 100

    track_charts = ["topsongs"]
    album_charts = ["newreleases", "justadded", "featuredalbums", "topalbums"]

    def parse(self, response):
        response = json.loads(response.body_as_unicode())
        for cc in response['feed_country']:
            if not "_" in cc:
                yield Request(url=self.available_feeds % cc,
                              callback=self.generate_feed_requests,
                              meta={'feed': {'cc': cc, 'cc_name': response['feed_country'][cc]}})


    def generate_url(self, prefix, cc=None, genre=None):
        if genre: return '{url}/genre={genre}'.format(url=prefix, genre=genre)
        if prefix and cc: return '{url}limit={limit}/cc={cc}'.format(url=prefix, limit=self.max_items, cc=cc)
        return None

    def generate_feed_requests(self, response):
        requests = []
        json_response = json.loads(response.body_as_unicode().replace("availableFeeds=", ""))
        meta = response.meta['feed']

        for cat in json_response['list']:
            if cat['name'] != "Music":
                continue

            for chart in cat['types']['list']:
                if 'topimixes' in chart['urlPrefix']:
                    continue
                url = self.generate_url(prefix=chart['urlPrefix'], cc=meta['cc'])
                meta['name'] = chart['display']
                requests.append(Request("{url}/{suffix}".format(url=url, suffix=chart['urlSuffix']),
                                        callback=self.__parse_as_chart__,
                                        meta=meta))

                for genre_chart in cat['genres']['list']:
                    genre_id = genre_chart['value']
                    if len(genre_id.strip()) != 0:
                        genre_url = self.generate_url(prefix=url, genre=genre_id)
                        meta['genre'] = genre_chart['display']
                        requests.append(Request("{url}/{suffix}".format(url=genre_url, suffix=chart['urlSuffix']),
                                                callback=self.__parse_as_chart__,
                                                meta=meta))
        for req in requests:
            yield req

    def do_create_chart(self, chart, response):
        name = response.meta['name']
        c_type = self.extract_type_from_url(response.url)
        c_geo = response.meta['cc_name']
        c_desc = "%s %s %s" % (c_geo, name, c_type)

        chart.add_value("name", name)
        chart.add_value("type", c_type)
        chart.add_value("geo", c_geo)
        chart.add_value("description", c_desc)

        if 'genre' in response.meta:
            genre = response.meta['genre']
            c_id = genre
            chart.add_value("description", "%s in %s" % (c_desc, genre))

        chart.add_value("id", name+c_id+c_geo)
        return chart

    def do_parse(self, chart, response):
        selector = Selector(response=response)
        selector.register_namespace('itms', 'http://phobos.apple.com/rss/1.0/modules/itms/')
        selector.register_namespace('ns', 'http://www.w3.org/2005/Atom')
        selector.register_namespace('im','http://itunes.apple.com/rss')

        itms = selector.xpath("//item")
        im = selector.xpath("/ns:feed/ns:entry")

        if itms: ns = 'itms'
        if im: ns = 'im'

        items = itms or im
        item_type = self.do_get_type(chart)

        for rank, item in enumerate(items):
            entry = TomahawkItemLoader(selector=item)
            if ns is 'im':
                entry.add_xpath(item_type, '//im:name/text()')
                entry.add_xpath('artist', './/im:artist/text()')
            else:
                entry.add_xpath('album', './/itms:album/text()')
                entry.add_xpath('artist', './/itms:artist/text()')
            entry.add_value('rank', rank)
            chart.add_value("list", entry.load_item())

        return self.do_process_item(chart)