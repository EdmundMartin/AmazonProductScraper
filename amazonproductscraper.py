import asyncio
import logging
from urllib.parse import urljoin

import aiohttp

from scraping_utils.random_headers import random_headers
from scraping_utils.random_proxies import RandomProxies
from scraping_utils.amazon_parsers import amazon_uk_product_parser


class AmazonProductScraper:

    def __init__(self, product_manifest, base_url='https://www.amazon.co.uk/', **kwargs):

        self.base_url = base_url
        self.product_list = self.__load_product_manifest(product_manifest)
        self.concurrency = kwargs.get('concurrency') if kwargs.get('concurrency') else 1
        self.proxies = RandomProxies(proxy_file=kwargs.get('proxy_file'))
        self.timeout = kwargs.get('timeout') if kwargs.get('timeout') else 30
        self.scrape_results = []

    def __load_product_manifest(self, product_manifest):

        with open(product_manifest, 'r', encoding='utf-8') as manifest:
            return [urljoin(self.base_url, product.strip()) for product in manifest]

    async def request_wrapper(self, url, **kwargs):
        async with aiohttp.ClientSession() as session:
            print(url)
            try:
                async with asyncio.BoundedSemaphore(self.concurrency), session.get(url, headers=random_headers(),
                                                                                   proxy=self.proxies.get(),
                                                                                   timeout=self.timeout) as response:
                    html = await response.read()
                    return {'url': url, 'new_url': response.url, 'response': html, 'task': 'success'}
            except aiohttp.ClientError:
                logging.error('Aiohtpp client error for {}'.format(url))
                return {'url': url, 'task': 'failed'}
            except Exception:
                logging.error('Unexpected error for {}'.format(url))
                return {'url': url, 'status': 418, 'task': 'failed'}

    async def amazon_css_parser(self, response):
        if response.get('response'):
            response = await amazon_uk_product_parser(response)
            return response
        return response

    async def main_wrapper(self, url, **kwargs):
        response = await self.request_wrapper(url, **kwargs)
        data = await self.amazon_css_parser(response)
        return data

    async def handle_tasks(self, url_list):
        scrape_results = []
        tasks = [self.main_wrapper(url, compres=True) for url in url_list]
        for result in await asyncio.gather(*tasks):
            scrape_results.append(result)
        self.scrape_results.extend(scrape_results)

    def run_scraper(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait([self.handle_tasks(self.product_list)]))
        loop.close()
        return self.scrape_results
