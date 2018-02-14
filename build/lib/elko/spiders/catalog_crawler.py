import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from selenium import webdriver
from selenium.webdriver.support.select import Select
from elko.items import ElkoItem
import lxml.html as lh


class BboSpider(scrapy.Spider):
    name = "main_catalog"
    login_page = "https://ecom.elko.ru/Account/Login?ReturnUrl=%2fCatalog%2fCategory%2fSCO"
    category_name = ''

    def __init__(self, category='', *args, **kwargs):
        super(BboSpider, self).__init__(*args, **kwargs)
        self.category_name = category

        self.driver = webdriver.PhantomJS()

    def start_requests(self):
        self.login_page = self.login_page[:-3] + self.category_name
        self.driver = webdriver.PhantomJS()
        self.driver.get(self.login_page)
        self.driver.find_element_by_id("Username").send_keys("tiscom6")
        self.driver.find_element_by_id("Password").send_keys("6307860")
        self.driver.find_element_by_name("submit").click()
        cookies = self.driver.get_cookies()

        yield scrapy.Request("https://ecom.elko.ru/Catalog/Category/SCO", cookies=self.driver.get_cookies(), callback=self.parse)

    def parse(self, response):
        select = Select(self.driver.find_element_by_xpath("//div[@class='quantity']/select"))
        select.select_by_value('100')
        doc = lh.fromstring(self.driver.page_source)
        page_count = doc.xpath("//div[@class='pages']/a")

        if len(page_count) > 0:

            for _ in range(len(page_count)):
                next_page = self.driver.find_element_by_xpath("//span[@class='icon fa fa-arrow-right fa-silver']")
                doc = lh.fromstring(self.driver.page_source)
                rows = doc.xpath("//table[@class='products favorite']/tbody[1]/tr[(.)]")
                for row in rows:
                    l = ItemLoader(item=ElkoItem(), response=response)
                    l.add_value("na_sklade", row.xpath("./td[7][@class='c nowrap']/span[1]/text()"))
                    l.add_value("price", row.xpath("./td[9][@class='price']/strong[2]/text()"))
                    l.add_value("code_elko", row.xpath("./td[1][@class='c']/text()"))
                    l.add_value("manufacture", row.xpath("./td[5]/text()"))
                    l.add_value("code_manufacture", row.xpath("./td[2][@class='c']/text()"))
                    l.add_value("title", row.xpath(
                        "./td[4][@class='title']/h4[1]/div[1]/a[1]/text()"),
                                )
                    yield l.load_item()

                next_page.click()

        else:
            doc = lh.fromstring(self.driver.page_source)
            rows = doc.xpath("//table[@class='products favorite']/tbody[1]/tr[(.)]")
            for row in rows:
                l = ItemLoader(item=ElkoItem(), response=response)
                l.add_value("na_sklade", row.xpath("./td[7][@class='c nowrap']/span[1]/text()"))
                l.add_value("price", row.xpath("./td[9][@class='price']/strong[2]/text()"))
                l.add_value("code_elko", row.xpath("./td[1][@class='c']/text()"))
                l.add_value("manufacture", row.xpath("./td[5]/text()"))
                l.add_value("code_manufacture", row.xpath("./td[2][@class='c']/text()"))
                l.add_value("title", row.xpath(
                    "./td[4][@class='title']/h4[1]/div[1]/a[1]/text()")
                           )
                yield l.load_item()


    def close(self, spider):

        self.driver.quit()



