# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticleSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
class JobBoleArticleItem(scrapy.Item):
    title=scrapy.Field()
    time=scrapy.Field()
    url=scrapy.Field()
    url_object_id=scrapy.Field()
    front_image_url=scrapy.Field()
    front_image_path=scrapy.Field()
    author=scrapy.Field()
    upvote=scrapy.Field()
    type=scrapy.Field()
    collection=scrapy.Field()
    comment=scrapy.Field()
