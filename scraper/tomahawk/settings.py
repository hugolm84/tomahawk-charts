# Scrapy settings for tomahawk_scraping project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

import os


BOT_NAME = 'tomahawk'
LOG_LEVEL = 'DEBUG'
COOKIES_ENABLED = False
RETRY_ENABLED = False
AJAXCRAWL_ENABLED = True
TEMPLATES_DIR = os.getcwd()+'/tomahawk/templates'
SPIDER_MODULES = ['tomahawk.spiders']
NEWSPIDER_MODULE = 'tomahawk.spiders'
DEFAULT_ITEM_CLASS = 'tomahawk.items.TomahawkItem'

ITEM_PIPELINES = {
    'tomahawk.pipelines.TomahawkScrapingPipeline' : 1
}
DOWNLOADER_MIDDLEWARES = {
    'tomahawk.middleware.OauthMiddleware.OauthMiddleware': 400,
    'scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware': 401,
}

USER_AGENT = 'Tomahawk Chart Service (+http://www.gettomahawk.com)'
FEED_FORMAT = 'json'
FEED_STORE_EMPTY = True
