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
import logging as log


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
        elif match_any(val, self.artist_charts):
            return self.ArtistType
        elif match_any(val, self.track_charts):
            return self.TrackType
        return None

    def extract_type_from_url(self, url):
        origin = unslugify(url)
        for word in origin.split("/"):
            type_from_origin = self.type_from_name(word) or self.match_type_fuzzy(word)
            if type_from_origin:
                self.log("Extracted type using origin (%s => %s) <GET %s>" % (word, type_from_origin, origin),
                         log.WARNING)
                return type_from_origin

        self.log("Failed to extract type using origin SPLIT <GET %s>" % (origin),
                 log.WARNING)
        return None

    def extract_type(self, chart):
        name = chart.get_output_value("name")

        type_from_name = self.type_from_name(name)
        if type_from_name:
            return type_from_name

        fuzzy = self.match_type_fuzzy(name)
        if fuzzy:
            return fuzzy

        return self.extract_type_from_url(chart.get_output_value("origin"))

    def type_from_name(self, name):
        try:
            return next(val for key, val in self.__types.iteritems() if key.lower() in name.lower())
        except StopIteration:
            None

    def make_sig_md5(self):
        import time
        import hashlib
        pre_sig = self.apiKey+self.apiSecret+str(int(time()))
        m = hashlib.md5()
        m.update(pre_sig)
        return m.hexdigest()

    def signed_url(self, method, args, request_args=None):
        import urllib
        args['apikey'] = self.apiKey
        args['sig'] = self.make_sig_md5()
        return "%s%s?%s%s" % (self.baseUrl,method, urllib.urlencode(args),
                              request_args if request_args is not None else "")
