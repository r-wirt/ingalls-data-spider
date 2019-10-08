# -*- coding: utf-8 -*-
from scrapy import Spider
from ingalls_data.items import IngallsDataItem
from scrapy.http import Request
from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-setuid-sandbox')

#MongoDB Index setup
#db.articles.createIndex({ title: "text", publisher:"text", lang:"text" } )
class IngallsSpider(Spider):
    name = 'ingalls'
    allowed_domains = ['library.clevelandart.org']
    start_urls = ['https://archive.org/details/clevelandmuseumofartIngallslibrary',
                   'https://archive.org/details/clevelandmuseumofartIngallslibrary?&sort=-downloads&page=2',
                   'https://archive.org/details/clevelandmuseumofartIngallslibrary?&sort=-downloads&page=3',
                   'https://archive.org/details/clevelandmuseumofartIngallslibrary?&sort=-downloads&page=4',
                   'https://archive.org/details/clevelandmuseumofartIngallslibrary?&sort=-downloads&page=5']

    def __init__(self, *args, **kwargs):
        global chrome_options
        self.driver = webdriver.Chrome('/Users/wirt_tre/Downloads/chromedriver', chrome_options=chrome_options)


    def parse(self, response):

        self.driver.get(response.request.url)
        res = response.replace(body=self.driver.page_source)
        document_urls  = response.xpath('//div[@class="C234"]//a/@href').extract()

        for document in document_urls:

            yield Request('http://archive.org' + document, callback=self.parse_product, dont_filter=True)

    def parse_product(self, response):
        source_url = response.xpath('//meta[@property="og:url"]/@content').extract_first()
        title = response.xpath('//span[@itemprop="name"]/text()').extract_first()
        author = response.xpath('//dl[dt/text()="by"]/dd/span/a/text()').extract_first()
        year_published = response.xpath('//span[@itemprop="datePublished"]/text()').extract_first()

        if year_published == '[date of publication not identified]':
            year_published = None

        elif year_published == None:
            year_published = None

        #If it gets to this condition, it's a digit
        #If the year is represented as something such as 1901 - 1909
        #Shorten to only 4 characters, and turn the year into an integer
        elif len(year_published) > 4:
            year_published = int(year_published[:4])




        publisher = response.xpath('//span[@itemprop="publisher"]/text()').extract_first()
        keywords = response.xpath('//dd[@itemprop="keywords"]/a/text()').extract()
        language = response.xpath('//dl[dt/text()="Language"]/dd/span/a/text()').extract_first()
        image = response.xpath('//meta[@property="og:image"]/@content').extract_first()


        load_item = IngallsDataItem()

        load_item['title'] = title
        load_item['author'] = author
        load_item['year'] = year_published
        load_item['image'] = image
        load_item['lang'] = language
        load_item['publisher'] = publisher
        load_item['keywords'] = keywords
        load_item['sourceurl'] = source_url
        #Returns object with each load_item included
        yield load_item
