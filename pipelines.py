# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline  # 调用下载图片的模块
import pymysql
from pymysql import cursors
from twisted.enterprise import adbapi
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok,value in results:
            image_file_path=value["path"]
        item["front_image_path"]=image_file_path
        return item
class MysqlPipline(object):
    # 同步并写入MySQL
    def process_item(self,item,spider):
        con=pymysql.connect(host="127.0.0.1",user="root",passwd="",db="test",charset="utf8")
        cue=con.cursor()
        print("MySQL connect sucess!")
        sql="INSERT INTO article_spider(title,time,url,url_object_id,front_image_url,front_image_path,type,author,upvote,collection,comment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        title=item['title']
        time=item['time']
        url=item['url']
        url_object_id=item['url_object_id']
        front_image_url=item['front_image_url']
        front_image_path=item['front_image_path']
        type=item['type']
        author=item['author']
        upvote=item['upvote']
        collection=item['collection']
        comment=item['comment']
        try:
            cue.execute(sql,[title,time,url,url_object_id,front_image_url,front_image_path,type,author,upvote,collection,comment])
            con.commit()
            print("Insert sucess!")
            return item
        except Exception as e:
            con.rollback()
        # 关闭数据库游标
        cue.close()
        # 关闭数据库链接
        con.close()

class MySQLTwistedPipline(object):
    # 异步读取MySQL
    @classmethod
    def from_settings(cls,settings):
        dbparms=dict(
        host=settings["MYSQL_HOST"],
        db=settings["MYSQL_DBNAME"],
        user=settings["MYSQL_USER"],
        passwd=settings["MYSQL_PASSWORD"],
        charset='utf8',
        cursorclass=cursors.Cursor,
        use_unicode=True
        )
        dbpool=adbapi.ConnectionPool("pymysql",**dbparms)
        return cls(dbpool)
    def __init__(self,dbpool):
        self.dbpool=dbpool
    def process_item(self,item,spider):
        # 使用twised将mysql插入变成异步调用
        query=self.dbpool.runInteraction(self.insert_item,item)
        # query.addErrback(self.handler_error,item,spider)  # 处理异常
        return item
    def handler_error(self,failure,item,spider):
        # 处理异步插入异常
        print(failure)
    def insert_item(self,cursor,item):
        # 执行具体的插入
        sql="""
            INSERT INTO article_spider(title,time,url,url_object_id,front_image_url,type,author,upvote,collection,comment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE upvote=VALUES(upvote),collection=VALUES(collection),comment=VALUES(comment)
            """
        item['front_image_url']=('').join(item['front_image_url'])
        item['type']=(',').join(item['type'])
        # item['author']
        cursor.execute(sql,(item['title'],item['time'],item['url'],item['url_object_id'],item['front_image_url'],item['type'],item['author'],item['upvote'],item['collection'],item['comment']))
