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
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class TomahawkChartItem(Item):
    #Required
    id, name, description, source, origin, type, list, size = (Field(),)*8
    #Optional
    have_extra, geo, genre = (Field(),)*3
    #Automatic
    parse_start_date, parse_end_date, expires = (Field(),)*3


class TomahawkItem(Item):
    rank, artist, album, track, stream_url = (Field(),)*5
