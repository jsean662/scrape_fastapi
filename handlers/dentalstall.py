import logging
from datetime import datetime

import requests
from lxml import html


logger = logging.getLogger("scrape_fastapi")


class DentalStallHandler():
    BASE_URL = 'https://dentalstall.com/shop/page/'
    LIMIT = 1
    OFFSET = 1
    PROXY = None
    
    def __init__(self, limit=LIMIT, offset=OFFSET, proxy=PROXY):
        self.LIMIT = limit
        self.OFFSET = offset
        self.PROXY = proxy
    
    def get_products(self):
        while self.OFFSET <= self.LIMIT:
            yield self._get_products_page()
            self.OFFSET += 1
    
    def _get_proxy(self):
        return {
            "http": self.PROXY,
            "https": self.PROXY
        } if self.PROXY else None
    
    # Retry 3 times before giving up, with increments of 30, 60 and 90 seconds
    def _make_request(self, url):
        for i in range(1, 3):
            try:
                return requests.get(url, proxies=self._get_proxy(), timeout=30 * i)
            except:
                logger.warn(f'Failed to get products from {url}. Retrying with {30 * (i + 1)} seconds timeout.')
        
        error_msg = f'Failed to get products from {url} after 3 retries.'
        logger.error(error_msg)
        raise Exception(error_msg)


    def _get_product_img(self, product):
        return product.xpath('div/div[1]/a/img/@data-lazy-src')[0]
    
    def _get_product_short_title(self, product):
        return product.xpath('div/div[2]/div[1]/h2/a/text()')[0]
    
    def _get_product_url(self, product):
        return product.xpath('div/div[2]/div[1]/h2/a/@href')[0]
    
    def _get_product_code(self, product):
        return self._get_product_url(product).split('/')[-2]
    
    def _get_product_full_title(self, product):
        return self._get_product_code(product).replace('-', ' ').title()
    
    def _get_product_price(self, product):
        try:
            return product.xpath('div/div[2]/div[2]/span[1]/ins/span/bdi/text()')[0]
        except:
            try:
                return product.xpath('div/div[2]/div[2]/span[1]/span[2]/bdi/text()')[0]
            except:
                return product.xpath('div/div[2]/div[2]/span/span/bdi/text()')[0]
        
    def _get_products_page(self):
        url = f'{self.BASE_URL}{self.OFFSET}/'
        logger.info(f'Getting products from {url}')

        page = self._make_request(url)
        tree = html.fromstring(page.content)
        products = tree.xpath('//*[@id="mf-shop-content"]/ul/li')
        result = {}
        for product in products:
            img = self._get_product_img(product)
            short_title = self._get_product_short_title(product)
            url = self._get_product_url(product)
            code = self._get_product_code(product)
            full_title = self._get_product_full_title(product)
            price = self._get_product_price(product)

            result[code] = {
                "code": code, # Added code to the response for easy identification of the product
                "product_title": full_title,
                "short_title": short_title,
                "path_to_image": img,               # TODO: save file to local storage
                "product_url": url,
                "product_price": price,
                "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        return result