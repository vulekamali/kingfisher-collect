from datetime import timedelta

from kingfisher_scrapy.util import parameters
from kingfisher_scrapy.base_spider import SimpleSpider


class Kosovo(SimpleSpider):
    """
    Domain
      Public Procurement Regulatory Commission
    Spider arguments
      from_date
        Download only data from this time onward (YYYY-MM-DDThh:mm:ss format). Defaults to '2000-01-01T00:00:00'.
      until_date
        Download only data until this time (YYYY-MM-DDThh:mm:ss format). Defaults to now.
    API documentation
      https://ocdskrpp.rks-gov.net/Help
    """
    name = 'kosovo'

    # BaseSpider
    date_format = 'datetime'
    date_required = True
    default_from_date = '2000-01-01T00:00:00'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        # The API is slow even with short periods, so we request one day at a time
        delta = self.until_date - self.from_date
        for days in reversed(range(delta.days + 1)):
            start = self.from_date + timedelta(days=days-1)
            end = self.from_date + timedelta(days=days)
            yield self.build_request(
                    'https://ocdskrpp.rks-gov.net/krppapi/tenderrelease?endDateFrom='
                    f'{start.strftime("%Y-%m-%d")}&endDateEnd={end.strftime("%Y-%m-%d")}',
                    formatter=parameters('endDateFrom', 'endDateEnd')
            )
