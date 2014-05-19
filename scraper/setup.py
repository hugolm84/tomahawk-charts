# Automatically created by: scrapy deploy

from setuptools import setup, find_packages

setup(
    name         = 'Tomahawk Scraper',
    version      = '1.0',
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = tomahawk.settings']},
)
