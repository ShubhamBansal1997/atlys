from typing import List, Optional, Tuple
import re
import tempfile
from lxml import html
from app.models import Product
from app.utils import download_image
from lxml.html import document_fromstring
from app.db import InMemoryDB
from app.notification import LogNotificationStrategy
from app.utils import make_request_with_proxy

# TODO: Ideally be replaced to a db connection in the future
DATA_FILE = f'{tempfile.gettempdir()}/scraped_data.json'
db = InMemoryDB(DATA_FILE)

class Scraper:
    def __init__(self, limit: int, proxy: str):
        # TODO: Most of these parameters can be part of initializing variable but ignoring due to time constraint
        self.base_url = "https://dentalstall.com/shop/page/{page_no}/"
        self.initial_page = 1
        self.limit = limit
        self.proxy = proxy
        self.proxies = {"http": proxy.replace("https://", "http://"), "https": proxy.replace("http://", "https://")}
        self.max_retries = 2
        self.delay_in_retry = 5
        self.notification_strategy = LogNotificationStrategy()
        self.xpath_to_title = './/h2[@class="woo-loop-product__title"]'
        self.xpath_to_price = [
            './/div[@class="mf-product-details"]/div[@class="mf-product-price-box"]/span[@class="price"]/ins/span[@class="woocommerce-Price-amount amount"]/bdi',
            './/div[@class="mf-product-details"]/div[@class="mf-product-price-box"]/span[@class="price"]/span[@class="woocommerce-Price-amount amount"]/bdi']
        self.xpath_to_img = './/div[@class="mf-product-thumbnail"]/a/img'
        self.img_key_attribute = "data-lazy-src"
        self.xpath_to_block = '//div[@class="product-inner  clearfix"]'
    
    def get_root(self, res) -> html.HtmlElement:
        try:
            root = document_fromstring(res.text)
        except ValueError:
            root = document_fromstring(res.content)
        return root
    
    @staticmethod
    def clean_title(content: str) -> str:
        # TODO: try to make clean functions generic as more fields are introduced
        content = re.sub('\n', '', content)
        content = re.sub('\r', '', content)
        content = re.sub('\t', '', content)
        content = re.sub('[ ]+', ' ', content)
        return content
    
    @staticmethod
    def clean_price(content: str) -> str:
        content = re.findall(r'\d+\.\d{1,2}|\d+', content)
        return content[0]
    
    def get_title(self, html_node: html.HtmlElement) -> str:
        title_tag = html_node.xpath(self.xpath_to_title)[0] 
        title = self.clean_title(title_tag.text_content())
        return title
    
    def get_price(self, html_node: html.HtmlElement) -> Optional[str]:
        for xpath in self.xpath_to_price:
            price_tag = html_node.xpath(xpath)
            if len(price_tag) > 0:
                price = self.clean_price(price_tag[0].text_content())
                return price
    
    def get_image(self, html_node: html.HtmlElement) -> str:
        # There are few edge cases which I am ignoring due to time constraint
        # 1. Base encoded images
        # 2. Uploading images to Object storage like S3
        # 3. Images which failed on the download
        img_tag = html_node.xpath(self.xpath_to_img)[0]
        img_url, img_path = "", ""
        for k, v in img_tag.items():
            if k == self.img_key_attribute:
                img_url = v
                break
        print("img_url", img_url)
        if img_url:
            img_path = download_image(img_url)
        return img_path
    

    def save_to_db(self, products: List[Product]) -> List[Product]:
        save_products = []
        for product in products:
            if not db.find_record(product.hash_key):
                db.save_new_record(product)
                save_products.append(product)
        return save_products
    
    def scrape(self) -> Tuple[List[Product], List[Product], List[str]]:
        total_products_scraped = []
        total_products_saved = []
        failed_requests = []
        for i in range(self.initial_page, self.limit):
            url = self.base_url.format(page_no=i)
            res = make_request_with_proxy(url, self.proxies, self.delay_in_retry, self.max_retries)
            if not res or res.status_code != 200:
                failed_requests.append(url)
            else:
                root = self.get_root(res)
                blocks = root.xpath(self.xpath_to_block)
                extracted_products = [Product(product_price=self.get_price(block), product_title=self.get_title(block), path_to_image=self.get_image(block)) for block in blocks]
                total_products_scraped.extend(extracted_products)
                saved_products = self.save_to_db(extracted_products)
                total_products_saved.extend(saved_products)
        self.notification_strategy.send_notification([total_products_scraped, total_products_saved, failed_requests])
        return total_products_scraped, total_products_saved, failed_requests
