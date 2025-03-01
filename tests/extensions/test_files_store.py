import logging
import os
from tempfile import TemporaryDirectory
from unittest.mock import Mock

import pytest
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy.extensions import FilesStore
from kingfisher_scrapy.items import File, FileItem
from tests import response_fixture, spider_with_crawler, spider_with_files_store


@pytest.fixture
def change_to_tmpdir(tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)


def test_from_crawler_missing_arguments():
    spider = spider_with_crawler()

    with pytest.raises(NotConfigured) as excinfo:
        FilesStore.from_crawler(spider.crawler)

    assert str(excinfo.value) == 'FILES_STORE is not set.'


@pytest.mark.parametrize('job', [None, '7df53218f37a11eb80dd0c9d92c523cb'])
def test_spider_opened(job, tmpdir):
    spider = spider_with_files_store(tmpdir)
    if job:
        spider._job = job

    extension = FilesStore.from_crawler(spider.crawler)
    extension.spider_opened(spider)

    path = tmpdir.join('test', '20010203_040506', 'scrapyd-job.txt')

    if job:
        with open(path)as f:
            assert f.read() == job
    else:
        assert not os.path.exists(path)


def test_spider_closed_odd_length(caplog, change_to_tmpdir):
    spider = spider_with_files_store('1')
    extension = FilesStore.from_crawler(spider.crawler)

    item = spider.build_file_from_response(response_fixture(), file_name='file.json', data_type='release_package')
    extension.item_scraped(item, spider)

    with caplog.at_level(logging.INFO):
        extension.spider_closed(spider, 'finished')

        assert [record.message for record in caplog.records] == [
            '+----------------- DATA DIRECTORY -----------------+',
            '|                                                  |',
            f'| The data is available at: 1{os.sep}test{os.sep}20010203_040506 |',
            '|                                                  |',
            '+--------------------------------------------------+',
        ]


def test_spider_closed_even_length(caplog, change_to_tmpdir):
    spider = spider_with_files_store('22')
    extension = FilesStore.from_crawler(spider.crawler)

    item = spider.build_file_from_response(response_fixture(), file_name='file.json', data_type='release_package')
    extension.item_scraped(item, spider)

    with caplog.at_level(logging.INFO):
        extension.spider_closed(spider, 'finished')

        assert [record.message for record in caplog.records] == [
            '+------------------ DATA DIRECTORY ------------------+',
            '|                                                    |',
            f'| The data is available at: 22{os.sep}test{os.sep}20010203_040506  |',
            '|                                                    |',
            '+----------------------------------------------------+',
        ]


def test_spider_closed_no_data(tmpdir, caplog):
    spider = spider_with_files_store(tmpdir)
    extension = FilesStore.from_crawler(spider.crawler)

    with caplog.at_level(logging.INFO):
        extension.spider_closed(spider, 'finished')

        assert [record.message for record in caplog.records] == [
            '+---------------- DATA DIRECTORY ----------------+',
            '|                                                |',
            '| Something went wrong. No data was downloaded.  |',
            '|                                                |',
            '+------------------------------------------------+',
        ]


def test_spider_closed_failed(tmpdir, caplog):
    spider = spider_with_files_store(tmpdir)
    extension = FilesStore.from_crawler(spider.crawler)

    with caplog.at_level(logging.INFO):
        extension.spider_closed(spider, 'failed')

        assert not caplog.records


@pytest.mark.parametrize('sample,path', [
    (None, os.path.join('test', '20010203_040506', 'file.json')),
    ('true', os.path.join('test_sample', '20010203_040506', 'file.json')),
])
def test_item_scraped_with_build_file_from_response(sample, path, tmpdir):
    spider = spider_with_files_store(tmpdir, sample=sample)
    extension = FilesStore.from_crawler(spider.crawler)

    response = Mock()
    response.body = b'{"key": "value"}'
    response.request = Mock()
    response.request.url = 'https://example.com/remote.json'
    response.request.meta = {'file_name': 'file.json'}

    item = spider.build_file_from_response(response, file_name='file.json', data_type='release_package')
    extension.item_scraped(item, spider)

    with open(tmpdir.join(path)) as f:
        assert f.read() == '{"key": "value"}'

    assert item['path'] == path


@pytest.mark.parametrize('sample,directory', [
    (None, os.path.join('test', '20010203_040506')),
    ('true', os.path.join('test_sample', '20010203_040506')),
])
@pytest.mark.parametrize('data', [b'{"key": "value"}', {"key": "value"}])
@pytest.mark.parametrize('item,expected_file_name', [
    (File({'file_name': 'file.json'}), 'file.json'),
    (FileItem({'number': 1, 'file_name': 'file.json'}), 'file-1.json')
])
def test_item_scraped_with_file_and_file_item(sample, directory, data, item, expected_file_name, tmpdir):
    spider = spider_with_files_store(tmpdir, sample=sample)
    extension = FilesStore.from_crawler(spider.crawler)

    path = os.path.join(directory, expected_file_name)
    original_file_name = item['file_name']
    item['data'] = data
    extension.item_scraped(item, spider)

    with open(tmpdir.join(path)) as f:
        assert f.read() == '{"key": "value"}'

    assert item['path'] == path
    assert item['file_name'] == original_file_name


def test_item_scraped_with_build_file_and_existing_directory():
    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        spider = spider_with_crawler(settings={'FILES_STORE': files_store})
        extension = FilesStore.from_crawler(spider.crawler)
        item = spider.build_file(file_name='file.json', data=b'{"key": "value"}')

        os.makedirs(os.path.join(files_store, 'test', '20010203_040506'))

        # No FileExistsError exception.
        extension.item_scraped(item, spider)
