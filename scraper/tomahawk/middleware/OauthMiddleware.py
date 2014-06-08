"""
    This Middleware module performs oauth2 requests
    Enable in DOWNLOADER_MIDDLEWARES
    Add the attributes oauth_key and oauth_consumer_secret to your spider class
    Make a regular Request but assign meta={'method_args: '...'}
"""

from scrapy import signals
import oauth2 as oauth
from scrapy.http.response import Response
import urllib

class OauthMiddleware(object):

    oauth_client = None

    @classmethod
    def from_crawler(cls, crawler):
        o = cls()
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        key = getattr(spider, 'oauth_key', None)
        secret = getattr(spider, 'oauth_consumer_secret', None)
        if key and secret:
            self.oauth_client = oauth.Client(oauth.Consumer(key, secret))

    def spider_closed(self, spider):
        if self.oauth_client:
            self.oauth_client = None

    def process_request(self, request, spider):
        if self.oauth_client:
            request_url = request._get_url()
            method_args = urllib.urlencode(request.meta['oauth_method_args'])
            header, content = self.oauth_client.request(request_url,
                                           request.method,
                                           method_args
            )
            if request.method == "POST":
                request_url = request_url+method_args
                request._set_url(request_url)

            return Response(request_url, header['status'], headers=header, body=content, request=request)