# coding=utf-8
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from selenium import webdriver
from selenium.webdriver.support.select import Select
from w3lib.html import replace_escape_chars

from elko.items import ElkoItem, ProductItems

import lxml.html as lh
class BboSpider(scrapy.Spider):
    name = "product_crawler"
    login_page = "https://ecom.elko.ru/Account/Login?ReturnUrl=%2fCatalog%2fCategory%2fSER"
    category_name = ''
    def __init__(self,category='', *args, **kwargs):
        super(BboSpider, self).__init__(*args,**kwargs)
        self.category_name=category

        self.driver = webdriver.PhantomJS()

    def start_requests(self):
        self.login_page = self.login_page[:-3] + self.category_name
        self.driver = webdriver.PhantomJS()
        self.driver.get(self.login_page)
        self.driver.find_element_by_id("Username").send_keys("blabla")
        self.driver.find_element_by_id("Password").send_keys("blabla")
        self.driver.find_element_by_name("submit").click()
        cookies = self.driver.get_cookies()
        yield scrapy.Request("https://ecom.elko.ru/", cookies=cookies)

    def parse(self, response):
        select = Select(self.driver.find_element_by_xpath("//div[@class='quantity']/select"))
        select.select_by_value('100')
        elem = self.driver.find_elements_by_xpath("//div[@class='pages']/a")

        if len(elem) is not 0:
            for _ in range(len(elem)):
                next_page = self.driver.find_element_by_xpath("//span[@class='icon fa fa-arrow-right fa-silver']")
                doc = lh.fromstring(self.driver.page_source)
                urls=[]
                for elements in doc.xpath(
                        "//table[@class='products favorite']/tbody[1]/tr[(.)]/td[4][@class='title']/h4[1]/div[1]/a[1]/@href"):
                    url = response.urljoin(elements)
                    urls.append(url)

                for url in urls:
                    yield scrapy.Request(url, callback=self.parse_item)
                next_page.click()
        else:
            doc = lh.fromstring(self.driver.page_source)
            for elements in doc.xpath(
                    "//table[@class='products favorite']/tbody[1]/tr[(.)]/td[4][@class='title']/h4[1]/div[1]/a[1]/@href"):
                url = response.urljoin(elements)
                yield scrapy.Request(url, callback=self.parse_item)

    def parse_item(self,response):
        l = ItemLoader(item=ProductItems(), response=response)
        l.add_value("title", response.xpath(
            "//div[@class='content']/h2/text()").extract())
        l.add_xpath("title", "//section[@class='product']/h2/text()")
        l.add_xpath("case_type",
           u"//table[@class='details']/tbody/tr[not(@class)][td[1]/text()[normalize-space() = 'Тип корпуса']]/td[2]/span[1][@class='black']/text()")

        yield l.load_item()
        for elem in response.xpath("//table[@class='details']/tbody/tr[not(@class)]"):
            l = ItemLoader(item=ProductItems(), response=response)
            l.add_value("value", elem.xpath("./td[2]/span[1][@class='black']/text()").extract())
            l.add_value("key", elem.xpath(u"./td[1]/text()").extract())
            yield l.load_item()
    def close(self, spider):
        self.driver.quit()
