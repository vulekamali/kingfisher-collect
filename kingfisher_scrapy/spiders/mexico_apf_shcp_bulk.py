import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error


class MexicoAPFSHCPBulk(CompressedFileSpider):
    """
    Domain
      Administración Pública Federal (APF) - Secretaría de Hacienda y Crédito Público (SHCP)
    Bulk download documentation
      https://datos.gob.mx/busca/dataset/concentrado-de-contrataciones-abiertas-de-la-apf-shcp
    """
    name = 'mexico_apf_shcp_bulk'

    # BaseSpider
    root_path = 'item'

    # CompressedFileSpider
    data_type = 'release'

    def start_requests(self):
        yield scrapy.Request(
            'https://drive.google.com/uc?id=1dHsnijrC_IQyGn0eY4ZzFwDLiJ-8kpS3',
            meta={'file_name': 'confirmation.html'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        url = response.xpath('//a[@id="uc-download-link"]/@href').get()
        yield self.build_request(url=f'https://drive.google.com{url}',
                                 formatter=components(-1),
                                 meta={'file_name': 'contrataciones.zip'})
