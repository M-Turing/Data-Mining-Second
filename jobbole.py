# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from article_spider.items import JobBoleArticleItem
from article_spider.utils.common import get_md5
import datetime
class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']
    def parse(self, response):
        post_nodes=response.xpath('//div[@class="post floated-thumb"]/div[@class="post-thumb"]').extract()
        regex_url='.*?href="(.*?)".*'
        regex_image_url='.*?src="(.*?)".*'
        for post_node in post_nodes:
            post_node=post_node.replace('\r','').replace('\n','').replace('\t','')
            post_url=re.match(regex_url,post_node)
            post_url=post_url.group(1)
            image_url=re.match(regex_image_url,post_node)
            image_url=image_url.group(1)
            image_url=parse.urljoin(response.url,image_url)
            yield Request(url=parse.urljoin(response.url,post_url),meta={'front_img_url':image_url},callback=self.parse_detail)  # 完成域名的拼接,yeild的作用就是将url给scrapy的下载器进行下载。。
        next_url=response.xpath('//a[@class="next page-numbers"]/@href').extract_first(default='')
        if next_url:
            yield Request(url=parse.urljoin(response.url,next_url),callback=self.parse)
        else:
            print("爬取结束！！")
    def parse_detail(self,response):
        article_item=JobBoleArticleItem()
        front_image_url=response.meta.get('front_img_url','')
        title=response.xpath('//div[@class="entry-header"]/h1/text()').extract_first(default='Not-Found')
        time=response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract_first(default='Not-Found').replace('·','').strip()
        author=response.xpath('//div[@class="copyright-area"]/a[@target="_blank"]/text()').extract_first(default='Not-Found')
        upvote=response.xpath('//div[@class="post-adds"]/span[1]/h10/text()').extract_first(default='')
        if upvote:
            upvote=int(upvote)
        else:
            upvote=0
        collection=response.xpath('//div[@class="post-adds"]/span[2]/text()').extract_first(default='').strip()[:-3]
        if collection:
            collection=int(collection)
        else:
            collection=0
        comment=response.xpath('//div[@class="post-adds"]/a/span/text()').extract_first(default='').strip()[:-3]
        if comment:
            comment=int(comment)
        else:
            comment=0
        type=response.xpath('//p[@class="entry-meta-hide-on-mobile"]//a/text()').extract()
        type=[element for element in type if not element.strip().endswith('评论')]
        type_to=list(set(type))
        type_to.sort(key=type.index)
        type=type_to
        article_item['url']=response.url
        article_item['url_object_id']=get_md5(response.url)
        article_item['front_image_url']=[front_image_url] #有问 题
        article_item['title']=title
        try:
            time=datetime.datetime.strptime(time,"%Y/%m/%d").date()   # 后面的.date是为了保留年、月、日的！结果为字符串
        except Exception as e:
            time=datetime.datetime.now().date()
        article_item['time']=time
        article_item['type']=type   # 有问题
        article_item['author']=author
        article_item['upvote']=upvote
        article_item['collection']=collection
        article_item['comment']=comment
        yield article_item
