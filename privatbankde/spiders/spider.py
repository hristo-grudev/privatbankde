import scrapy

from scrapy.loader import ItemLoader

from ..items import PrivatbankdeItem
from itemloaders.processors import TakeFirst


class PrivatbankdeSpider(scrapy.Spider):
	name = 'privatbankde'
	start_urls = ['https://www.privatbank.de/archiv/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="teaserBanner__teaser js-click-item-parent"]')
		for post in post_links:
			url = 'https://www.privatbank.de/' + post.xpath('.//a/@href').get()
			date = post.xpath('.//time/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('//ul[@class="teaserBanner__pagination"]/li/a/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		if response.url[-1:] != r'/':
			return
		title = response.xpath('//h1[@class="textBlock__headline" or @class="intro__title"]/text()').get()
		description = response.xpath('//div[@class="content" or @class ="intro__text content" or class ="colContentImage content"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=PrivatbankdeItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
