import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import (append_path_components, browser_user_agent, components, handle_http_error, join,
                                    parameters, replace_parameters)


class Ukraine(SimpleSpider):
    """
    Domain
      ProZorro OpenProcurement API
    Caveats
      The API returns OCDS-like contracting processes data, however an ocid is not set. Therefore, as part of this
      spider, the data.tenderID is used as the ocid and the data.id + data.dateModified fields are used and release.id
    Spider arguments
      from_date
        Download only data from this time onward (YYYY-MM-DDThh:mm:ss format).
    API documentation
      https://prozorro-api-docs.readthedocs.io/uk/latest/tendering/index.html
    """
    name = 'ukraine'
    user_agent = browser_user_agent  # to avoid HTTP 412 errors

    # BaseSpider
    encoding = 'utf-16'
    data_type = 'release'
    date_format = 'datetime'
    ocds_version = '1.0'

    def start_requests(self):
        # A https://public.api.openprocurement.org/api/0/contracts endpoint also exists but the data returned from
        # there is already included in the tenders endpoint. If we would like to join both, the tender_id field from
        # the contract endpoint can be used with the id field from the tender endpoint.
        url = 'https://public.api.openprocurement.org/api/0/tenders'
        if self.from_date:
            url = f'{url}?offset={self.from_date.strftime(self.date_format)}'
        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        data = response.json()

        for item in data['data']:
            url = append_path_components(replace_parameters(response.request.url, offset=None), item['id'])
            yield self.build_request(url, formatter=components(-2))

        yield self.build_request(data['next_page']['uri'], formatter=join(components(-1), parameters('offset')),
                                 callback=self.parse_list)

    @handle_http_error
    def parse(self, response):
        data = response.json()['data']
        # The response looks like:
        # {
        #   "data": {
        #     "id": "..",
        #     "dateModified": "...",
        #     "tenderID": "",
        #     other tender fields,
        #     "awards": ...,
        #     "contracts": ...
        #    }
        # }

        awards = data.pop('awards', None)
        contracts = data.pop('contracts', None)

        ocds_data = {
            # `id` is an internal identifier. `dateModified` is appended to ensure the id's uniqueness.
            'id': f"{data['id']}-{data['dateModified']}",
            # `tenderID` is the official identifier.
            'ocid': data['tenderID'],
            'date': data['dateModified'],
            'tender': data,
        }
        if contracts:
            ocds_data['contracts'] = contracts
        if awards:
            ocds_data['awards'] = awards

        yield self.build_file_from_response(response, data=ocds_data, data_type=self.data_type)
