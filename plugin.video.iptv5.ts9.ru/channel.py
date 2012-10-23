#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.6
# -*- coding: utf-8 -*-


import os, time, xbmcaddon, xbmcvfs
import sqlite3 as sqlite

__addon__ = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')
addon_path = __addon__.getAddonInfo('path')

class Channel:
    def __init__(self):
        self.filename = os.path.join(addon_path, 'resources', 'channel.sqlite')

        self._connect()
        self.cur.execute('pragma auto_vacuum=1')
        self.cur.execute("CREATE TABLE IF NOT EXISTS channels (name TEXT, url TEXT, mimetype TEXT, category_id INTEGER, is_fav BOOLEAN DEFAULT '0' NOT NULL , is_broken BOOLEAN DEFAULT '0' NOT NULL )")
        self.db.commit()
        self._close()

    def find(self, url):
        self._connect()
        self.cur.execute("SELECT name,url,mimetype,category_id,is_fav FROM channels WHERE url=?", (url, ))
        result = [{'name': x[0], 'url': x[1], 'category_id' : x[2], 'is_fav' : x[3]} for x in self.cur.fetchall()][0]
        self._close()

        return result

    def exists(self, url):
        self._connect()
        self.cur.execute("SELECT EXISTS(SELECT 1 FROM channels WHERE url=? LIMIT 1)", (url, ))
        result = [x[0] for x in self.cur.fetchall()][0]
        self._close()
        return result

    def find_by_category_id(self, category_id):
        self._connect()
        self.cur.execute("SELECT name,url,mimetype FROM channels WHERE category_id=? AND is_broken=? ORDER BY name ASC", (category_id, 0))
        result = [[x[0],x[1],x[2]] for x in self.cur.fetchall()]
        self._close()
        return result

    def save(self, name, url,category_id, is_broken,mimetype):
        self.destroy(url)
        self._connect()
        self.cur.execute('INSERT INTO channels(name,url,mimetype,category_id, is_broken) VALUES(?,?,?,?,?)', (name, url,mimetype, category_id,is_broken))
        self.db.commit()
        self._close()

    def destroy(self, url):
        self._connect()
        self.cur.execute('DELETE FROM channels WHERE url=?', (url, ))
        self.db.commit()
        self._close()

    def favorites(self):
        self._connect()
        self.cur.execute("SELECT name,url,mimetype FROM channels WHERE is_fav=1 ORDER BY name ASC")
        result = [[x[0],x[1],x[2]] for x in self.cur.fetchall()]
        self._close()
        return result

    def addToFav(self, url):
        self._connect()
        self.cur.execute('UPDATE channels SET is_fav=1 WHERE url=?', (url, ))
        self.db.commit()
        self._close()

    def removeFromFav(self, url):
        self._connect()
        self.cur.execute('UPDATE channels SET is_fav=0 WHERE url=?', (url, ))
        self.db.commit()
        self._close()

    def _connect(self):
        try:
          self.db = sqlite.connect(self.filename)
          self.db.text_factory = str
          self.cur = self.db.cursor()
        except:
          raise "*** Cann't connect to channels DB !!!"

    def drop(self):
        if xbmcvfs.exists(self.filename):
            self._connect()
            self.cur.execute('DELETE FROM channels')
            self.db.commit()
            self._close()

    def _close(self):
        self.cur.close()
        self.db.close()
