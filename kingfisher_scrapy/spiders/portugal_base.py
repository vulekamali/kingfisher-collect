import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import parameters


class PortugalBase(LinksSpider):
    # BaseSpider
    default_from_date = '2010-01-01'
    # Every ~36,000 requests, the API returns HTTP errors. After a few minutes, it starts working again.
    # https://github.com/open-contracting/kingfisher-collect/issues/545#issuecomment-762768460
    # The spider waits 1, 2, 4, 8 and 16 minutes (31 minutes total) before retries.
    max_attempts = 6

    # LinksSpider
    formatter = staticmethod(parameters('offset'))

    # start_url must be provided by subclasses.

    def start_requests(self):
        url = self.start_url
        if self.from_date and self.until_date:
            url = f'{url}?contractStartDate={self.from_date.strftime(self.date_format)}' \
                  f'&contractEndDate={self.until_date.strftime(self.date_format)}'

        yield scrapy.Request(url, meta={'file_name': 'offset-1.json'})

    def is_http_retryable(self, response):
        return response.status != 404

    def get_retry_wait_time(self, response):
        return response.request.meta.get('wait_time', 30) * 2
