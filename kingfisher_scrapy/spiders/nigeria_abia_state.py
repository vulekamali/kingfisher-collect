from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.util import components


class NigeriaAbiaState(PeriodicSpider):
    """
    Domain
      Abia E-PROCUREMENT
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2018'.
      until_date
        Download only data until this year (YYYY format). Defaults to '2021'.
    Bulk download documentation
      https://abiaeprocurement.ab.gov.ng/ocds_report.php
    """
    name = 'nigeria_abia_state'

    # BaseSpider
    date_format = 'year'
    default_from_date = '2018'
    default_until_date = '2021'

    # PeriodicSpider
    pattern = 'http://abiaeprocurement.ab.gov.ng/media/ocds{}.json'

    # SimpleSpider
    data_type = 'release_package'

    def get_formatter(self):
        return components(-1)