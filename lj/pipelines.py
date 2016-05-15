from datetime import datetime
import json
import codecs
from collections import OrderedDict
from hashlib import md5, sha256
from scrapy import log
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi


class FilterWordsPipeline(object):
    """A pipeline for filtering out items which contain certain words in their
    description"""

    # put all words in lowercase
    words_to_filter = ['politics', 'religion']

    def process_item(self, item, spider):
        for word in self.words_to_filter:
            desc = item.get('description') or ''
            if word in desc.lower():
                raise DropItem("Contains forbidden word: %s" % word)
        else:
            return item


class RequiredFieldsPipeline(object):
    """A pipeline to ensure the item have the required fields."""

    required_fields = ('name', 'description', 'url')

    def process_item(self, item, spider):
        for field in self.required_fields:
            if not item.get(field):
                raise DropItem("Field '%s' missing: %r" % (field, item))
        return item


class MySQLStorePipeline(object):
    """A pipeline to store the item in a MySQL database.
    This implementation uses Twisted's asynchronous database API.
    """

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            connect_timeout=5,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        # run db query in the thread pool
        d = self.dbpool.runInteraction(self._do_upsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        # at the end return the item in case of success or failure
        d.addBoth(lambda _: item)
        # return the deferred instead the item. This makes the engine to
        # process next item (according to CONCURRENT_ITEMS setting) after this
        # operation (deferred) has finished.
        return d

    def _do_upsert(self, conn, item, spider):
        """Perform an insert or update."""
        guid = self._get_index(item)
        price = item['price']
        url = item['url']
        now = datetime.utcnow().replace(microsecond=0).isoformat(' ')

        update_sql = """
            UPDATE lj_pudong
            SET updated=%s
            WHERE guid=%s
        """
        inser_sql = """
            INSERT INTO lj_pudong (guid, url, location, area, layout, size,
            buildtime, price, created)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        ret = conn.execute("""SELECT EXISTS(
            SELECT 1 FROM lj_pudong WHERE guid = %s AND price = %s
            )""", (guid, price))
        ret = conn.fetchone()[0]

        if ret:
            conn.execute(update_sql, (now, guid))
            spider.log("Item stored in db: %s %r" % (guid, item))
        else:
            conn.execute(inser_sql, (guid, item['url'], item['location'],
                item['area'], item['layout'], item['size'], item['buildtime'],
                item['price'], now))
            spider.log("Item stored in db: %s %r" % (guid, item))

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log
        log.err(failure)

    def _get_guid(self, item):
        """Generates an unique identifier for a given item."""
        return md5(item['url']+item['price']).hexdigest()

    def _get_index(self, item):
        """Generates an unique identifier for a given item."""
        return item['price'] + item['url']

    def _close_spider(self, spider):
        """Close dbpool connection."""
        self.dbpool.close()


class JsonWithEncodingPipeline(object):

    def __init__(self):
        self.file = codecs.open('lj_pudong.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(OrderedDict(item), ensure_ascii=False, sort_keys=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()
