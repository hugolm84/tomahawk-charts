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

import os
from scrapy import signals
from scrapy.contrib.exporter import JsonLinesItemExporter, JsonItemExporter
from scrapy.exceptions import DropItem


class TomahawkScrapingPipeline(object):

    _feed_store = "items/%s/%s/"
    item_store = None
    source_exporter = None

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        store_path = self._feed_store % (spider.crawler.settings['BOT_NAME'], spider.name)
        self.item_store = self.create_spider_dir(store_path)
        #self.source_exporter = JsonItemExporter(open(self.item_store + "metadata.jl", "w"))
        #self.source_exporter.start_exporting()

    def spider_closed(self, spider):
        #self.source_exporter.finish_exporting()
        pass

    def create_spider_dir(self, store):
        if not os.path.exists(os.path.dirname(store)):
            os.makedirs(os.path.dirname(store))
        return store

    def export_item(self, item):
        item_exporter = JsonLinesItemExporter(open(self.item_store+item["id"], "w"))
        item_exporter.start_exporting()
        item_exporter.export_item(item)
        item_exporter.finish_exporting()

    def process_item(self, item, spider):
        if not item['id'] or len(item['id'].strip()) == 0:
            raise DropItem("Missing id: %s" % item)

        if not item['list'] or len(item['list']) == 0:
            raise DropItem("Missing list of items: %s" % item)

        # Store this item in a separate file
        self.export_item(item)
        # Remove the the large list, pass it along to scrapyd
        item.pop("list")
        return item
