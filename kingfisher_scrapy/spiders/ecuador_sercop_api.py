from kingfisher_scrapy.base_spiders import IndexSpider, PeriodicSpider
from kingfisher_scrapy.util import components, parameters


class EcuadorSERCOPAPI(PeriodicSpider, IndexSpider):
    """
    Domain
      Servicio Nacional de Contratación Pública (SERCOP)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2015'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
    API documentation
        https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/api
    Bulk download documentation
      https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos
    """
    name = 'ecuador_sercop_api'
    custom_settings = {
        # Reduce the number of concurrent requests to avoid multiple failures.
        'CONCURRENT_REQUESTS': 2,
        # Don't let Scrapy handle HTTP 429.
        'RETRY_HTTP_CODES': [],
    }

    # BaseSpider
    date_format = 'year'
    default_from_date = '2015'

    # SimpleSpider
    data_type = 'release_package'

    # Local
    max_attempts = 5
    retry_code = 429
    url_prefix = 'https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/api/'

    # PeriodicSpider
    formatter = staticmethod(components(-1))
    pattern = f'{url_prefix}search_ocds?year={{0}}'
    start_requests_callback = 'parse_list'

    # IndexSpider
    total_pages_pointer = '/pages'
    parse_list_callback = 'parse_page'

    def parse_list(self, response):
        if self.is_http_success(response):
            yield from super().parse_list(response)
        else:
            yield self.build_retry_request_or_file_error(response, int(response.headers['Retry-After']),
                                                         self.max_attempts, response.status == self.retry_code)

    def parse_page(self, response):
        if self.is_http_success(response):
            for data in response.json()['data']:
                # Some ocids have a '/' character which cannot be in a file name.
                yield self.build_request(f'{self.url_prefix}record?ocid={data["ocid"]}',
                                         formatter=lambda url: parameters('ocid')(url).replace('/', '_'))
        else:
            yield self.build_retry_request_or_file_error(response, int(response.headers['Retry-After']),
                                                         self.max_attempts, response.status == self.retry_code)

    def parse(self, response, **kwargs):
        if self.is_http_success(response):
            yield from super().parse(response)
        else:
            yield self.build_retry_request_or_file_error(response, int(response.headers['Retry-After']),
                                                         self.max_attempts, response.status == self.retry_code)
