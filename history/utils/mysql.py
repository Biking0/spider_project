# encoding:utf-8
import re
import json
import time
import traceback
from datetime import datetime, timedelta

import requests
try:
    import MySQLdb
except:
    import pymysql as MySQLdb

import settings


class MySql:
    """
    对数据库的一些操作
    """

    def __init__(self):
        self.db, self.cursor = self.gen_db()

    def add_li(self, item_list, table, only):
        """
        根据判断某些键是否存在来插入数据
        :param item_list: 要更新的数据
        :param table: 表名
        :param only: 判断是否存在的键
        :return:
        """
        if isinstance(item_list, dict):
            item_list = [item_list]
        for item in item_list:
            self.add_item(item, only, table)

    def add_item(self, item, only, table):
        sql = 'SELECT * FROM %s WHERE ' % table
        sql += ' AND '.join([('{}=%s'.format(k)) for k in only])
        if not self.db.open:
            self.db, self.cursor = self.gen_db()
        try:
            self.cursor.execute(sql, [item[k] for k in only])
        except Exception as e:
            print(e)
            print(sql)
        rows = self.cursor.fetchall()
        if len(rows):
            return
        self.insert(item, table)

    def get_series(self, id, ts):
        table_name = 'history_' + ts
        sql = 'SELECT * from %s WHERE bId = "%s"' % (table_name, id)
        if not self.db.open:
            self.db, self.cursor = self.gen_db()
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        series = []
        for item in data:
            id, depTime, addtime, seats, price, invalid, cabin, flightNumber, preTime = item
            series.append(dict(
                bId=id,
                depTime=depTime,
                addtime=addtime,
                seats=seats,
                price=price,
                invalid=invalid,
                cabin=cabin,
                flightNumber=flightNumber,
                preTime=preTime
            ))
        return series

    def get_id(self, carrier, ts):
        st_stamp = time.mktime(time.strptime(ts, '%Y%m%d'))
        en_stamp = st_stamp + 24 * 60 * 60
        sql = 'SELECT id FROM base_ticket WHERE carrier = "%s" AND depTime >= %s AND depTime < %s'\
              % (carrier, st_stamp, en_stamp)
        print(sql)
        if not self.db.open:
            self.db, self.cursor = self.gen_db()
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        for item in data:
            yield item[0]

    def insert(self, item, table):
        k_v = [[k, item[k]] for k in item if item[k]]
        keys = ','.join([k[0] for k in k_v])
        values = ','.join(['%s'] * len(k_v))
        sql = 'INSERT %s (%s) VALUES (%s)' % (table, keys, values)
        if not self.db.open:
            self.db, self.cursor = self.gen_db()
        try:
            self.cursor.execute(sql, [k[1] for k in k_v])
        except Exception as e:
            print(e)
            print(sql)

    def create_table(self, table_name):
        sql = 'show tables;'
        if not self.db.open:
            self.db, self.cursor = self.gen_db()
        self.cursor.execute(sql)
        tables = [self.cursor.fetchall()]
        table_list = re.findall('(\'.*?\')', str(tables))
        table_list = [re.sub("'", '', each) for each in table_list]
        if table_name in table_list:
            return
        sql = 'CREATE TABLE %s LIKE history_20190101;' % table_name
        self.cursor.execute(sql)

    def gen_db(self):
        while True:
            try:
                db = MySQLdb.connect(
                    host=settings.DB_HOST,
                    user=settings.DB_USER,
                    passwd=settings.DB_PWD,
                    db=settings.DB_NAME,
                    port=settings.DB_PORT,
                )
                db.autocommit(True)
                return db, db.cursor()
            except Exception as e:
                traceback.print_exc()
                print(e)
                time.sleep(5)


if __name__ == '__main__':
    db = MySql()
