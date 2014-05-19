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
import dateutil.parser
from datetime import datetime
from scrapy import log
from scrapy.contrib.loader.processor import arg_to_iter


class PassThrough(object):

    def __call__(self, values):
        return values


class Strip(object):

    def __call__(self, values):
        return [v.strip() for v in arg_to_iter(values)]


class Slugify(object):

    _slugify_strip_re = re.compile(r'[^\w\s-]')
    _slugify_hyphenate_re = re.compile(r'[-\s]+')

    def slugify(self, value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.
        From Django's "django/template/defaultfilters.py".
        """
        import unicodedata
        if not isinstance(value, unicode):
            value = unicode(value)
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        value = unicode(self._slugify_strip_re.sub('', value).strip().lower())
        return self._slugify_hyphenate_re.sub('-', value)

    def __call__(self, values):
        return [self.slugify(v) for v in arg_to_iter(values)]


class ListValidator(object):

    __req_fields = None

    def __init__(self, req_field):
        self.__req_fields = req_field

    def __call__(self, values):
        if self.__req_fields is None:
            return values

        out_value = []
        for v in arg_to_iter(values):
            if all(key.lower() in v.keys() for key in self.__req_fields):
                out_value.append(v)
            else :
                log.msg("Failed to validate %s => %s" % (v, self.__req_fields), level=log.CRITICAL)
        return out_value


class DateTime(object):

    __format = '%Y-%m-%d-%H:%M:%S.%f'

    def __init__(self, date_format=None):
        if date_format is None:
            date_format = self.__format
        self.format = date_format

    def __call__(self, values):
        out_values = []
        for v in arg_to_iter(values):
            if isinstance(v, (str, unicode)):
                try:
                    out_values.append(dateutil.parser.parse(str(v), fuzzy=True).strftime(self.format))
                except:
                    log.msg('Failed to convert datetime string: "%s"' % v, level=log.WARNING)
                    out_values.append(None)
            elif isinstance(v, datetime):
                out_values.append(v.strftime(self.format))
            else:
                out_values.append(datetime(v).strftime(self.format))
        return out_values
