# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
from six.moves.urllib.parse import quote
from tieba.items import ThreadItem, PostItem, CommentItem


class TiebaPipeline(object):
    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    def __init__(self, settings):
        dbname = settings['MYSQL_DBNAME']
        tbname = settings['TIEBA_NAME']
        if not dbname.strip():
            raise ValueError("No database name!")
        if not tbname.strip():
            raise ValueError("No tieba name!")

        self.settings = settings

        self.dbpool = adbapi.ConnectionPool('MySQLdb',
                                            host=settings['MYSQL_HOST'],
                                            db=settings['MYSQL_DBNAME'],
                                            user=settings['MYSQL_USER'],
                                            passwd=settings['MYSQL_PASSWD'],
                                            charset='utf8mb4',
                                            cursorclass=MySQLdb.cursors.DictCursor,
                                            # 异步容易冲突
                                            init_command='set foreign_key_checks=0'
                                            )

    def open_spider(self, spider):
        spider.cur_page = begin_page = self.settings['BEGIN_PAGE']
        spider.end_page = self.settings['END_PAGE']
        spider.filter = self.settings['FILTER']
        spider.see_lz = self.settings['SEE_LZ']
        tbname = self.settings['TIEBA_NAME']
        if not isinstance(tbname, bytes):
            tbname = tbname.encode('utf8')
        start_url = "http://tieba.baidu.com/f?kw=%s&pn=%d" \
                    % (quote(tbname), 50 * (begin_page - 1))
        if self.settings['GOOD_ONLY']:
            start_url += '&tab=good'

        spider.start_urls = [start_url]

    def close_spider(self, spider):
        self.settings['SIMPLE_LOG'].log(spider.cur_page - 1)

    def process_item(self, item, spider):
        _conditional_insert = {
            'thread': self.insert_thread,
            'post': self.insert_post,
            'comment': self.insert_comment
        }
        query = self.dbpool.runInteraction(_conditional_insert[item.name], item)
        query.addErrback(self._handle_error, item, spider)
        return item

    def insert_thread(self, tx, item):
        sql = "insert into t_thread values(%s, %s, %s, %s, %s,%s)"
        params = (item["id"], item["title"], item['author'], item['reply_num'], item['good'], 0)
        tx.execute(sql, params)

    def insert_post(self, tx, item):
        sql = "insert into t_post values(%s, %s, %s, %s, %s, %s, %s,%s)"
        params = (item["id"], item["floor"], item['author'], item['content'],
                  item['time'], item['comment_num'], item['thread_id'], 0)
        tx.execute(sql, params)

    def insert_comment(self, tx, item):
        tx.execute('set names utf8mb4')
        sql = "insert into t_comment values(%s, %s, %s, %s, %s,%s)"
        params = (item["id"], item['author'], item['content'], item['time'], item['post_id'], 0)
        tx.execute(sql, params)

    # 错误处理方法
    def _handle_error(self, fail, item, spider):
        spider.logger.error('Insert to database error: %s \
        when dealing with item: %s' % (fail, item))
