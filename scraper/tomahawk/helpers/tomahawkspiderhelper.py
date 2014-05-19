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

import re
from scrapy import log

_matches = lambda value, regexs: any((r.search(value) for r in regexs))

def unslugify(value):
    return value.replace('-', ' ').replace('_', ' ')

def match_any(value, values):
    return _matches(value, [re.compile(x, re.IGNORECASE) for x in values])

def extract(xpath, selector):
    try :
        return selector.xpath(xpath).extract()[0]
    except IndexError:
        return None

class TomahawkSpiderHelper(object):

    AlbumType = "Album"
    TrackType = "Track"
    ArtistType = "Artist"
    RankKey = "Rank"

    album_charts, artist_charts, track_charts = ([],)*3

    __types = {'album': AlbumType, 'track': TrackType, 'singles': TrackType, 'songs': TrackType, 'song': TrackType,
               'artist': ArtistType,
    }

    __track_item_req = [TrackType, ArtistType, RankKey]
    __artist_item_req = [ArtistType, RankKey]
    __album_item_req = [ArtistType, AlbumType, RankKey]

    __item_reqs = {TrackType : __track_item_req, ArtistType : __artist_item_req, AlbumType : __album_item_req}

    @staticmethod
    def get_item_reqs(type):
        return TomahawkSpiderHelper.__item_reqs.get(type.title())

    def match_type_fuzzy(self, val):
        if match_any(val, self.album_charts):
            return self.AlbumType
        if match_any(val, self.artist_charts):
            return self.ArtistType
        if match_any(val, self.track_charts):
            return self.TrackType
        return None

    def origin_to_name(self, origin):
        origin = origin.rsplit('/',1)[1]
        return unslugify(origin)

    def extract_type(self, chart):
        name = chart.get_output_value("name")
        origin = chart.get_output_value("origin")

        type_from_name = self.type_from_name(name)
        if type_from_name:
            return type_from_name

        fuzzy = self.match_type_fuzzy(name)
        if fuzzy:
            return fuzzy

        for word in self.origin_to_name(origin).split():
            type_from_origin = self.type_from_name(word)
            if type_from_origin:
                self.log("Extracted type using origin (%s => %s) <GET %s>" % (word, type_from_origin, origin),
                                 log.WARNING)
                return type_from_origin
        return None

    def type_from_name(self, name):
        try:
            return next(val for key, val in self.__types.iteritems() if key.lower() in name.lower())
        except StopIteration:
            None