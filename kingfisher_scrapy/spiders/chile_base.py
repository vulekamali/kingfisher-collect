import datetime
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class ChileCompraBaseSpider(BaseSpider):
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'DOWNLOAD_FAIL_ON_DATALOSS': False,
        'HTTPERROR_ALLOW_ALL': True,
    }
    download_timeout = 300
    limit = 100
    base_list_url = 'https://apis.mercadopublico.cl/OCDS/data/listaA%C3%B1oMes/{}/{:02d}/{}/{}'
    record_url = 'https://apis.mercadopublico.cl/OCDS/data/record/%s'
    base_file_name = 'year-{}-month-{:02d}-offset-{}-limit-{}.json'
    start_year = 2008

    def get_year_month_until(self):
        until_year = datetime.datetime.now().year + 1
        until_month = datetime.datetime.now().month
        if hasattr(self, 'year'):
            self.start_year = int(self.year)
            until_year = self.start_year + 1
            until_month = 12 if self.start_year != datetime.datetime.now().year else until_month
        return until_year, until_month

    def get_sample_request(self):
        return scrapy.Request(
                url=self.base_list_url.format(2017, 10, 0, 10),
                meta={'kf_filename': 'sample.json', 'year': 2017, 'month': 10}
            )

    def start_requests(self):
        if self.is_sample():
            yield self.get_sample_request()
            return
        until_year, until_month = self.get_year_month_until()
        for year in range(self.start_year, until_year):
            for month in range(1, 13):
                # just scrape until the current month when the until year = current year
                if (until_year - 1) == year and month > until_month:
                    break
                yield scrapy.Request(
                    url=self.base_list_url.format(year, month, 0, self.limit),
                    meta={'kf_filename': self.base_file_name.format(year, month, 0, self.limit),
                          'year': year, 'month': month}
                )

    def base_parse(self, response, package_type):
        data = json.loads(response.body_as_unicode())
        if 'data' in data:
            yield_list = []
            for data_item in data['data']:
                if package_type == 'record':
                    yield_list.append(scrapy.Request(
                        url=self.record_url % data_item['ocid'].replace('ocds-70d2nz-', ''),
                        meta={'kf_filename': 'data-%s-%s.json' % (data_item['ocid'], package_type)}
                    ))
                else:
                    # the data comes in this format:
                    # "data": [
                    #       {
                    #        "ocid": "",
                    #        "urlTender": "..",
                    #        "urlAward": ".."
                    #        }
                    #    ]
                    for stage in list(data_item.keys()):
                        if 'url' in stage:
                            name = stage.replace('url', '')
                            yield_list.append(scrapy.Request(
                                url=data_item[stage],
                                meta={'kf_filename': 'data-%s-%s.json' % (data_item['ocid'], name)}
                            ))
            if 'pagination' in data and (data['pagination']['offset'] + self.limit) < data['pagination']['total']:
                year = response.request.meta['year']
                month = response.request.meta['month']
                offset = data['pagination']['offset']
                yield_list.append(scrapy.Request(
                    url=self.base_list_url.format(year, month, self.limit + offset, self.limit),
                    meta={'year': year, 'month': month,
                          'kf_filename': self.base_file_name.format(year, month, offset, self.limit)}
                ))
            return yield_list
        else:
            return [self.save_response_to_disk(response, response.request.meta['kf_filename'],
                                               data_type='%s_package' % package_type)]