import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BbanescoItem
from itemloaders.processors import TakeFirst
import requests
from scrapy import Selector

pattern = r'(\xa0)?'

url = "https://www.banesco.com/wp-admin/admin-ajax.php"

payload = "action=dcms_ajax_filters&pag=6&filtro=notas"
headers = {
  'Connection': 'keep-alive',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'Accept': '*/*',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'Origin': 'https://www.banesco.com',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.banesco.com/category/somos-banesco/sala-de-prensa',
  'Accept-Language': 'en-US,en;q=0.9',
  'Cookie': '_ga=GA1.2.1784641153.1618922563; _gid=GA1.2.1215848653.1618922563; _gat=1'
}

response = requests.request("POST", url, headers=headers, data=payload)

class BbanescoSpider(scrapy.Spider):
	name = 'banesco'
	start_urls = ['https://www.banesco.com/category/somos-banesco/sala-de-prensa']

	def parse(self, response):
		data = requests.request("POST", url, headers=headers, data=payload)
		post_links = Selector(text=data.text).xpath('//a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		date = response.xpath('//meta[@property="article:published_time"]/@content').get().split('T')[0]
		title = response.xpath('//h2/text()').get()
		content = response.xpath('//div[@class="col-lg-24 col-md-24 col-sm-24 col-xs-24 detail-content some-class-name2"]//text()[not (ancestor::h2)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=BbanescoItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
