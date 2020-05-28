from kingfisher_scrapy.spiders.chile_base import ChileCompraBaseSpider


class ChileCompraRecords(ChileCompraBaseSpider):
    """
    Swagger API documentation
      https://desarrolladores.mercadopublico.cl/docs/services/5a9ed02f718ed712f4403e75/operations/data-listaa-omes-agno-mes?
    Spider arguments
      sample
        Download only data released on October 2017.
    """
    name = 'chile_compra_records'

    def parse(self, response):
        if response.status == 200:
            for item in self.base_parse(response, 'record'):
                yield item
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
