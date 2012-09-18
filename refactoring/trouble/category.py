#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.2
# -*- coding: utf-8 -*-

import os, datetime, xbmcaddon
import sqlite3 as sqlite
from datetime import timedelta

__addon__ = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')
addon_path = __addon__.getAddonInfo('path')

now = datetime.datetime.today()
if int(__addon__.getSetting('interval')) > 0:
    past = now - datetime.timedelta(hours=int(__addon__.getSetting('interval')))
else:
    past = now - datetime.timedelta(seconds=10)

print "Now " + str(now)
print "Next " + str(past)


class Category:
    def __init__(self):
        self.filename = os.path.join(addon_path, 'resources', 'category.sqlite')

        self._connect()
        self.cur.execute('pragma auto_vacuum=1')
        self.cur.execute("CREATE TABLE IF NOT EXISTS categories (created_at TIMESTAMP, name TEXT, optgroupid TEXT)")
        self.db.commit()
        self._close()

    def find(self, name):
        self._connect()
        self.cur.execute("SELECT name, optgroupid, created_at FROM categories WHERE name=?", (name, ))
        result = [{'name': x[0], 'optgroupid': x[1], 'created_at' : x[2]} for x in self.cur.fetchall()]
        self._close()
        return result[0]

    def exists(self, name):
        self._connect()
        self.cur.execute("SELECT EXISTS(SELECT 1 FROM categories WHERE name=? LIMIT 1)", (name, ))
        result = [x[0] for x in self.cur.fetchall()][0]
        self._close()

        return result

    def find_all(self):
        self._connect()
        self.cur.execute("SELECT name,optgroupid FROM categories ORDER BY name ASC")
        result = [{ x[0]: x[1] } for x in self.cur.fetchall()]
        self._close()
        return result

    # add timestamp and set it to last for initial scan
    def save(self, name, optgroupid, init):
        print "initial scan " + str(init)
        timestamp = past if init else now
        self.destroy(name)
        self._connect()
        self.cur.execute('INSERT INTO categories(created_at,name,optgroupid) VALUES(?,?,?)', (timestamp, name, optgroupid))
        self.db.commit()
        self._close()

    def destroy(self, name):
        self._connect()
        self.cur.execute('DELETE FROM categories WHERE name=?', (name, ))
        self.db.commit()
        self._close()

    def find_outdated(self):
        self._connect()
        self.cur.execute("SELECT optgroupid FROM categories WHERE created_at <=?", (past, ))
        result = [x[0] for x in self.cur.fetchall()]
        self._close()
        return result        

    def _connect(self):
        self.db = sqlite.connect(self.filename)
        self.db.text_factory = str
        self.cur = self.db.cursor()

    def _drop(self):
        self._connect()
        self.cur.execute('DROP TABLE IF EXISTS categories')
        self.db.commit()
        self._close()

    def _close(self):
        self.cur.close()
        self.db.close()
