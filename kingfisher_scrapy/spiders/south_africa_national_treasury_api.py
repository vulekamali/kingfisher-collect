import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import parameters


class SouthAfricaNationalTreasuryAPI(LinksSpider):
    """
    Domain
      South Africa National Treasury
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format). Defaults to '2021-05-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format). Defaults to today.
    Swagger API documentation
      https://ocds-api.etenders.gov.za/swagger/index.html
    """
    name = 'south_africa_national_treasury_api'

    # BaseSpider
    date_format = 'date'
    date_required = True
    default_from_date = '2021-05-01'

    # SimpleSpider
    data_type = 'release_package'

    # LinksSpider
    formatter = staticmethod(parameters('PageNumber'))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SouthAfricaNationalTreasuryAPI, cls).from_crawler(crawler, *args, **kwargs)

        spider.base_url = crawler.settings.get('KINGFISHER_ZA_NT_API_URL')

        return spider

    def start_requests(self):
        yield scrapy.Request(f'{self.base_url}?PageNumber=1&PageSize=50&'
                             f'dateFrom={self.from_date}&dateTo={self.until_date}', meta={'file_name': 'start.json'})
