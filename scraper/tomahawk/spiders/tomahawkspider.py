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

import datetime
import calendar

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.exceptions import ContractFail
from scrapy.utils.trackref import print_live_refs
from scrapy import signals

from w3lib.url import url_query_cleaner

from tomahawk.itemloaders import TomahawkChartLoader
from tomahawk.helpers.tomahawkspiderhelper import TomahawkSpiderHelper


class TomahawkCrawlSpider(TomahawkSpiderHelper,CrawlSpider):

    _spider = None
    __chart_items = {}
    # Default value 24h expiration (0-23)
    expires = 23

    @classmethod
    def from_crawler(cls, crawler,  **kwargs):
        ext = cls(**kwargs)
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    def spider_opened(self, spider):
        self._spider = spider
        print_live_refs()

    def spider_closed(self, spider):
        for key in self.__chart_items.keys():
            self.__chart_items[key] = None
        self.__chart_items = None
        self._spider = None
        print_live_refs()

    @staticmethod
    def follow_link(xpath, allow, deny, callback = None, cb_kwargs={}):
        return Rule (
            SgmlLinkExtractor(restrict_xpaths=(xpath,), allow=allow, deny=deny),
            follow=True, callback = callback, cb_kwargs=cb_kwargs
        )

    @staticmethod
    def follow_link_as_chart(xpath, allow = None, deny = None):
        return TomahawkCrawlSpider.follow_link(xpath, allow, deny, callback='__parse_as_chart__')

    @staticmethod
    def follow_link_as_next(xpath, allow = None, deny = None):
        return TomahawkCrawlSpider.follow_link(xpath, allow, deny, callback='__parse_as_next_page__')

    def do_parse(self, chart, response):
        raise NotImplementedError

    def do_create_chart(self, chart, response):
        raise NotImplementedError

    def do_process_item(self, chart):
        chart.add_value("size", len(chart.get_output_value("list")))
        chart.add_value("parse_end_date", datetime.datetime.utcnow())
        return chart.load_item()

    def do_get_type(self, chart):
        item_type = chart.get_output_value("type")
        if item_type is None:
            raise ContractFail("Failed to get item type for chart! (%s) <GET %s>"
                           % (chart.get_output_value("name"), chart.get_output_value("origin")))
        return item_type.lower()

    def __create_chart__(self, response):
        try:
            selector = Selector(response)
        except AttributeError:
            selector = None
        chart = TomahawkChartLoader(selector=selector)
        chart.add_value("origin", response.url)
        chart.add_value("source", {'spider': self.name})
        chart.add_value("parse_start_date", datetime.datetime.utcnow())
        chart.add_value("expires", self.expires_in())
        return self.do_create_chart(chart, response)

    def __parse_as_chart__(self, response):
        self.__chart_items[response.url] = self.__create_chart__(response)
        yield self.do_parse(self.__chart_items[response.url], response)

    def __parse_as_next_page__(self, response):
        refer = response.request.headers.get('Referer')
        chart = self.__chart_items[url_query_cleaner(refer)]
        yield self.do_parse(chart, response)

    def expires_in(self):
        future = datetime.datetime.utcnow() + datetime.timedelta(hours=self.expires)
        return  datetime.datetime.utcfromtimestamp(calendar.timegm(future.timetuple()))
