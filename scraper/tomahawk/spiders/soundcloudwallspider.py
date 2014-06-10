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

import json
from dateutil import rrule
from datetime import datetime as dt

from scrapy.http.request import Request
from tomahawkspider import TomahawkCrawlSpider, TomahawkSpiderHelper
from tomahawk.itemloaders import TomahawkItemLoader


class SoundCloudWallSpider(TomahawkCrawlSpider):

    name = "Soundcloudwall"
    #http://www.soundcloudwall.com/api/chart/<year>/<month>
    #http://www.soundcloudwall.com/api/chart/2011/october
    baseUrl = "http://www.soundcloudwall.com/api/chart/"
    baseTitle = "100 Most Influential Tracks of"
    apiKey = "TiNg2DRYhBnp01DA3zNag"

    start_date = "201105"
    end_date = "201308"

    def start_requests(self):
        # Create url for each month between start_date and end_date
        for dtg in rrule.rrule(rrule.MONTHLY,dtstart=dt.strptime(self.start_date, '%Y%m'),
                until=dt.strptime(self.end_date, '%Y%m')):

            month = dtg.strftime("%B")
            yield Request("%s%s/%s" % (self.baseUrl, dtg.year, month.lower()),
                          callback=self.__parse_as_chart__,
                          meta={"year": dtg.year, "month": month})

    def do_create_chart(self, chart, response):
        name = "%s %s-%s" % (self.baseTitle, response.meta['year'], response.meta['month'])
        chart.add_value("name", name)
        chart.add_value("type", TomahawkSpiderHelper.TrackType)
        chart.add_value("description", "SoundCloudWall publishes a playlist of the 1000 most influential tracks on "
                                       "SoundCloud each month.")
        return chart

    def parse_metadata(self, item, delimiters):
        # Soundcloud metadata is hard
        title = item.pop("title").rstrip().strip()
        metadata = {}
        for delimiter in delimiters:
            if not metadata:
                try:
                    metadata["artist"] = title[:title.index(delimiter)]
                    metadata["track"] = title[title.index(delimiter)+len(delimiter):]
                except ValueError, e:
                    continue
            else:
                break

        if not metadata:
            metadata['artist'] = item.pop("username").rstrip().strip()
            metadata['track'] = title
        return metadata

    def do_parse(self, chart, response):
        j = json.loads(response.body_as_unicode())
        delimiters = [" - ", " -", ": ", ":", "\u2014"]
        for rank, item in enumerate(j):
            if rank < 100:
                metadata = self.parse_metadata(item, delimiters)
                entry = TomahawkItemLoader()
                entry.add_value("track", metadata.pop('track'))
                entry.add_value("artist",metadata.pop("artist"))
                entry.add_value("rank", rank)
                chart.add_value("list", entry.load_item())
            else:
                break
        return self.do_process_item(chart)
