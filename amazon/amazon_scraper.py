import time
from dataclasses import dataclass
from functools import cached_property

from fake_useragent import UserAgent
from requests_html import HTML
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver


def get_user_agent():
    ua = UserAgent(verify_ssl=False)
    return ua.random

@dataclass
class AmazonScraper():
    
    url: str 
    driver: WebDriver = None
    headless: bool = True
    endless_scroll: bool = False
    endless_scroll_pause: int = 4

    def __post_init__(self):
        self.driver = self.get_driver()

    def get_driver(self) -> WebDriver:
        if self.driver is None:
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument(f'user-agent={get_user_agent()}')
            self.driver = webdriver.Chrome(options=options)
        return self.driver

    def perform_endless_scroll(self) -> None:
        current_height = self.driver.execute_script("return document.body.scrollHeight")
        if self.endless_scroll:
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(self.endless_scroll_pause)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == current_height:
                    break
                current_height = new_height

    def get_page(self) -> str:
        self.driver.get(self.url)
        self.perform_endless_scroll()
        return self.driver.page_source

    @cached_property
    def html_obj(self) -> HTML:
        return HTML(html=self.get_page())

    def get_product_title(self) -> str:
        selector = '#productTitle'
        return self.html_obj.find(selector, first=True).text

    def get_product_price(self) -> str:
        selector = '.apexPriceToPay span'
        return self.html_obj.find(selector, first=True).text

    def get_product_extra_details(self) -> dict:
        selector = "table[class='a-normal a-spacing-micro']"
        extra_details_table = self.html_obj.find(selector, first=True)
        rows = extra_details_table.find("tr")
        extra_details = {}
        for row in rows:
            key,value = row.text.split("\n")
            extra_details[key.strip()] = value.strip()
        return extra_details
