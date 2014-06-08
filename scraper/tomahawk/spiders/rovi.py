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

from tomahawkspider import TomahawkCrawlSpider
from tomahawk.helpers.tomahawkspiderhelper import TomahawkSpiderHelper
from tomahawk.itemloaders import TomahawkItemLoader
from operator import itemgetter
import datetime
import json
from scrapy.http import Request

class RoviSpider(TomahawkCrawlSpider):

    name = 'Rovi'

    baseUrl = "http://api.rovicorp.com/"
    apiKey = "7jxr9zggt45h6rg2n4ss3mrj"
    apiSecret = "XUnYutaAW6"
    daysAgo = 365
    maxAlbums = 100
    baseArgs = {
        "entitytype": "album",
        "facet": "genre",
        "size": "600",
        "offset": "0",
        "country": "US",
        "format": "json"
    }
    releases_filter = "&filter=releaseyear>:%s" % (datetime.datetime.now().year-1)
    editorial_filter = "%s%s" % (releases_filter, "&filter=editorialrating>:7")
    # Rovi allows 5 reqs per second (add extra 0.05 for fail safe)
    download_delay = 0.25

    def __init__(self, *args, **kwargs):
        super(RoviSpider, self).__init__(*args, **kwargs)
        self.start_urls = [self.__signed_url(
            method = "data/v1/descriptor/musicgenres",
            args = {
                "country": "US",
                "format": "json",
                "language": "en"
            })
        ]

    def __signed_url_for_genre(self, genre_id, filter_query):
        args = self.baseArgs
        args["filter"] = "genreid:%s" % (genre_id)
        return self.__signed_url(method="search/v2/music/filterbrowse", args=args,  filter_query=filter_query)

    def parse(self, response):
        '''
            Overload scrapy parse, as we create new urls for each genre
        '''
        j = json.loads(response.body_as_unicode())
        genres = [(item['id'], item['name']) for item in j['genres']]
        requests_to_yield = []

        for genre in genres:
            requests_to_yield.append(Request(self.__signed_url_for_genre(genre[0], self.releases_filter),
                                             callback=self.__parse_as_chart__,
                                             meta={'genre': genre, 'type': 'New Album Releases'}))
            requests_to_yield.append(Request(self.__signed_url_for_genre(genre[0], self.editorial_filter),
                                             callback=self.__parse_as_chart__,
                                             meta={'genre': genre, 'type': 'Editorial Choice'}))

        for req in requests_to_yield:
            yield req

    def do_create_chart(self, chart, response):
        name = response.meta['genre'][1]
        identifier = response.meta['type']
        chart.add_value("id", identifier+name)
        chart.add_value("name", name)
        chart.add_value("type", TomahawkSpiderHelper.AlbumType)
        chart.add_value("description", identifier)
        return chart

    def do_parse(self, chart, response):
        j = json.loads(response.body_as_unicode())
        status = j['searchResponse']['controlSet']['status'].strip()
        if status != 'ok':
            return None

        for entry, rank in enumerate(self.get_list_from_result(j)):
            entry = TomahawkItemLoader()
            entry.add_value("artist", entry['artist'])
            entry.add_value("album", entry['title'])
            entry.add_value("rank", rank)
            chart.add_value("list", entry.load_item())

        return self.do_process_item(chart)

    def get_list_from_result(self, json_result):
        chart_list = []
        null_list = []
        for rank, album in enumerate(json_result['searchResponse']['results']):
            try:
                album = album['album']
                title = album['title']
                artist = " ".join([ artist['name'] for artist in album['primaryArtists'] ])
                release_date = album['originalReleaseDate']
                rating = album['rating']

                # instead of filter out by releasedate, we search the api by releaseyear
                # the result seems to be more appealing
                # Note: some albums have Null releaseDate, this doesnt necessarily mean
                # that the release date isnt within our range. We include some of them as well
                if release_date is not None :
                    chart_list.append (
                        {'album': title,
                         'artist': artist,
                         'date': release_date,
                         'rating': rating
                        })
                else :
                    null_list.append (
                        {'album': title,
                         'artist': artist,
                         'date': release_date,
                         'rating': rating
                        })
            except Exception, e:
                print e
                continue

        if len(null_list) > self.maxAlbums:
            print("Slicing NUllList from %s to %s" %(len(null_list), self.maxAlbums))
            nullList = null_list[-self.maxAlbums:]

        chart_list = sorted(chart_list, key=itemgetter('date'))

        if len(chart_list) > self.maxAlbums :
            print("Slicing list from %s to %s" %(len(chart_list), self.maxAlbums))
            chart_list = chart_list[-self.maxAlbums:]

        return nullList + chart_list
