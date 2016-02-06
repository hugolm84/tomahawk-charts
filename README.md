#Tomahawk Charts

Contains the scrapers/crawlers and webserivce that powers Tomahawk Player charts.

Refer to docs/scrapers to add/manage scrapers

##Basic Environment Setup
[Read more about virtualenv @readthedocs.org](http://virtualenvwrapper.readthedocs.org/en/latest/)

##Setup a virtualenv to separate your env's (valid for OSX, perhaps others to):
    $ easy_install pip
    $ pip install virtualenv
    $ pip install virtualenvwrapper

##Update your .bash_profile:
    #virtualenv
    export WORKON_HOME=~/.virtualenvs
    source /usr/local/bin/virtualenvwrapper.sh
    export PIP_VIRTUALENV_BASE=$WORKON_HOME
    export PIP_RESPECT_VIRTUALENV=true

    $ source .bash_profile

##Create virtualenv:
    $ mkvirtualenv --no-site-packages scraper

##Switch to virtualenv
    $ workon scraper

##Install dependencies
Compiling C modules on OSX using Xcode 5.1 we need to set some flags to not default to error on unknown args: [see stackoverflow](https://stackoverflow.com/questions/22703393/clang-error-unknown-argument-mno-fused-madd-wunused-command-line-argumen)

    (scraper)$ export CFLAGS=-Qunused-arguments
    (scraper)$ export CPPFLAGS=-Qunused-arguments
    (scraper)$ pip install -r requirements.txt

### Failing to build requirements
If you fail to build requirement on osx, check if xcode command tools is installed:

    $ xcode-select --install

##Create a spider
Creating spiders should be as straight forward as

    scrapy genspider -t tomahawk MySpider MySpider.com

##Deploy
Create egg file of the project

###Start scrapyd

    (scraper)$ scrapyd

###Deploy

    (scraper)$ scrapyd-deploy
    scrapyd-deploy default -p tomahawk
    Packing version r47-master
    Deploying to project "tomahawk" in http://localhost:6800/addversion.json
    Server response (200):
    {"status": "ok", "project": "tomahawk", "version": "r47-master", "spiders": 9, "node_name": "spider-server"}

###Schedule a scrape

    (scraper)$ curl http://localhost:6800/schedule.json -d project=tomahawk -d spider=Billboard

###References:
    http://virtualenvwrapper.readthedocs.org/en/latest/
    http://www.jontourage.com/2011/02/09/virtualenv-pip-basics/
    http://blog.sidmitra.com/manage-multiple-projects-better-with-virtuale

