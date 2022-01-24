import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.exceptions import KingfisherScrapyError
from kingfisher_scrapy.util import handle_http_error


class IndiaCivicDataLab(SimpleSpider):
    """
    Domain
      CivicDataLab
    Bulk download documentation
      https://github.com/CivicDataLab/himachal-pradesh-health-procurement-OCDS/
    """
    name = 'india_civic_data_lab'

    github_repo = 'CivicDataLab/himachal-pradesh-health-procurement-OCDS'

    # BaseSpider
    unflatten = True
    unflatten_args = {
        'metatab_name': 'Meta',
        'metatab_vertical_orientation': True
    }

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        url = f'https://api.github.com/repos/{self.github_repo}/git/trees/master'
        yield scrapy.Request(url, meta={'file_name': 'response.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        # Use the GitHub API to list the files in the repository, and then download the files using a non-API method,
        # to avoid quota/rate limits.

        data = response.json()
        # https://docs.github.com/en/rest/reference/git#get-a-tree
        if data['truncated']:
            raise KingfisherScrapyError('Truncated results returned when querying the file list from GitHub')

        for node in data['tree']:
            file_name = node['path']
            if file_name.endswith('.xlsx'):
                url = f'https://github.com/{self.github_repo}/raw/master/{file_name}?raw=true'
                yield scrapy.Request(url, meta={'file_name': file_name})
