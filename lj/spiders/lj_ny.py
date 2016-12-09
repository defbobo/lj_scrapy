import scrapy

from lj.items import LjItem

class LjNySpider(scrapy.Spider):
    name = "lj_ny"
    start_urls = (
        'http://sh.lianjia.com/ershoufang/pudongxinqu/p1/',
        'http://sh.lianjia.com/ershoufang/pudongxinqu/p2/',
        'http://sh.lianjia.com/ershoufang/pudongxinqu/p3/',
        'http://sh.lianjia.com/ershoufang/pudongxinqu/p7/',
        'http://sh.lianjia.com/ershoufang/pudongxinqu/c1p4/',
        'http://sh.lianjia.com/ershoufang/pudongxinqu/c2p4/',
        'http://sh.lianjia.com/ershoufang/pudongxinqu/c3p4/',
        'http://sh.lianjia.com/ershoufang/pudongxinqu/c1p6/',
        'http://sh.lianjia.com/ershoufang/pudongxinqu/c2p6/',
        'http://sh.lianjia.com/ershoufang/pudongxinqu/c3p6/',
        'http://sh.lianjia.com/ershoufang/pudongxinqu/c1p8/',
        'http://sh.lianjia.com/ershoufang/pudongxinqu/c2p8/',
        'http://sh.lianjia.com/ershoufang/pudongxinqu/c3p8/',
        'http://sh.lianjia.com/ershoufang/pudongxinqu/b300to400c1',
        'http://sh.lianjia.com/ershoufang/pudongxinqu/b300to400c2',
        'http://sh.lianjia.com/ershoufang/pudongxinqu/b300to400c3',
        'http://sh.lianjia.com/ershoufang/pudongxinqu/b401to500c1',
        'http://sh.lianjia.com/ershoufang/pudongxinqu/b401to500c2',
        'http://sh.lianjia.com/ershoufang/pudongxinqu/b401to500c3',
    )

    def clean_item(self, link_text):
        return link_text.strip()

    def parse(self, response):
        url_prefix = 'http://sh.lianjia.com/'
        item = LjItem()
        data = response.xpath('//li/div[@class="info-panel"]')
        for house in data:
            url = house.xpath('h2/a/@href').extract()
            location = house.xpath('div/div[@class="where"]/a/span/text()'
                                   ).extract()
            area = house.xpath('div/div[@class="other"]/div/a[2]/text()'
                               ).extract()
            layout = house.xpath('div/div[@class="where"]/span/text()'
                                 ).extract()
            buildtime = house.xpath(
                'div/div[@class="other"]/div/text()[last()]').extract()
            price = house.xpath('div[@class="col-3"]/div/span/text()'
                                ).extract()
            size = house.xpath('div/div[@class="where"]/span[2]/text()').extract()
            item['url'] = self.clean_item(url[0])
            item['location'] = self.clean_item(location[0])
            item['area'] = self.clean_item(area[0])
            item['layout'] = self.clean_item(layout[0])
            item['buildtime'] = self.clean_item(buildtime[0])
            item['price'] = self.clean_item(price[0])
            item['size'] = self.clean_item(size[0])
            yield item

        house_listbox = response.xpath(
            '//div[@class="page-box house-lst-page-box"]/a[@href]')
        next_url = url_prefix + house_listbox[-1].xpath('@href').extract()[0]

        yield scrapy.Request(next_url, callback=self.parse)
