
import os
from glob import glob
from tempfile import TemporaryDirectory

import pytest
from scrapy import Request
from scrapy.exceptions import StopDownload

from kingfisher_scrapy.extensions import KingfisherPluck
from kingfisher_scrapy.items import PluckedItem
from tests import spider_with_crawler


def test_disabled():
    with TemporaryDirectory() as tmpdirname:
        spider = spider_with_crawler(settings={'KINGFISHER_PLUCK_PATH': tmpdirname})
        extension = KingfisherPluck.from_crawler(spider.crawler)
        item = PluckedItem({'value': '2020-10-01'})

        extension.item_scraped(item, spider)
        extension.spider_closed(spider, 'itemcount')

        assert not glob(os.path.join(tmpdirname, 'pluck*.csv'))


def test_item_scraped():
    with TemporaryDirectory() as tmpdirname:
        spider = spider_with_crawler(settings={'KINGFISHER_PLUCK_PATH': tmpdirname}, release_pointer='/date')
        extension = KingfisherPluck.from_crawler(spider.crawler)
        item = PluckedItem({'value': '2020-10-01'})

        extension.item_scraped(item, spider)

        with open(os.path.join(tmpdirname, 'pluck-release-date.csv')) as f:
            assert '2020-10-01,test\n' == f.read()

        # Only one item from the same spider is written.
        extension.item_scraped(item, spider)

        with open(os.path.join(tmpdirname, 'pluck-release-date.csv')) as f:
            assert '2020-10-01,test\n' == f.read()

        # An item from another spider is appended.
        spider.name = 'other'
        item['value'] = '2020-10-02'
        extension.item_scraped(item, spider)

        with open(os.path.join(tmpdirname, 'pluck-release-date.csv')) as f:
            assert '2020-10-01,test\n2020-10-02,other\n' == f.read()


def test_spider_closed_with_items():
    with TemporaryDirectory() as tmpdirname:
        spider = spider_with_crawler(settings={'KINGFISHER_PLUCK_PATH': tmpdirname}, release_pointer='/date')
        extension = KingfisherPluck.from_crawler(spider.crawler)
        item = PluckedItem({'value': '2020-10-01'})

        extension.item_scraped(item, spider)
        extension.spider_closed(spider, 'itemcount')

        with open(os.path.join(tmpdirname, 'pluck-release-date.csv')) as f:
            assert '2020-10-01,test\n' == f.read()


def test_spider_closed_without_items():
    with TemporaryDirectory() as tmpdirname:
        spider = spider_with_crawler(settings={'KINGFISHER_PLUCK_PATH': tmpdirname}, release_pointer='/date')
        extension = KingfisherPluck.from_crawler(spider.crawler)

        extension.spider_closed(spider, 'itemcount')

        with open(os.path.join(tmpdirname, 'pluck-release-date.csv')) as f:
            assert 'closed: itemcount,test\n' == f.read()


def test_bytes_received_stop_download():
    with TemporaryDirectory() as tmpdirname:
        spider = spider_with_crawler(settings={'KINGFISHER_PLUCK_PATH': tmpdirname,
                                               'KINGFISHER_PLUCK_MAX_BYTES': 1}, release_pointer='/date')
        extension = KingfisherPluck.from_crawler(spider.crawler)
        request = Request('http://example.com', meta={'file_name': 'test.json'})

        with pytest.raises(StopDownload):
            extension.bytes_received(data={'test': 'test'}, spider=spider, request=request)

        assert extension.max_bytes == 1


def test_bytes_received_dont_stop_download():
    with TemporaryDirectory() as tmpdirname:
        spider = spider_with_crawler(settings={'KINGFISHER_PLUCK_PATH': tmpdirname,
                                               'KINGFISHER_PLUCK_MAX_BYTES': 10}, release_pointer='/date')
        extension = KingfisherPluck.from_crawler(spider.crawler)
        request = Request('http://example.com', meta={'file_name': 'test.json'})

        extension.bytes_received(data={'test': 'test'}, spider=spider, request=request)
        assert extension.bytes_received_per_spider[spider.name] == 1

        assert extension.max_bytes == 10
