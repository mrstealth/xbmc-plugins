#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.2
# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-


import os, time, xbmcaddon
import sqlite3 as sqlite

__addon__ = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')
addon_path = __addon__.getAddonInfo('path')

class Channel:
    def __init__(self, filename):
        self.filename = os.path.join(addon_path, 'resources', 'channel.sqlite')

        self._connect()
        self.cur.execute('pragma auto_vacuum=1')
        self.cur.execute("CREATE TABLE IF NOT EXISTS channels (name TEXT, url TEXT, category_id INTEGER)")
        self.db.commit()
        self._close()

    def find(self, url):
        self._connect()
        self.cur.execute("SELECT name, url, category_id FROM channels WHERE url=?", (url, ))
        result = [{'name': x[0], 'url': x[1], 'category_id' : x[2]} for x in self.cur.fetchall()]
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
        self.cur.execute("SELECT name, url, category_id FROM channels WHERE category_id=?", (category_id, ))
        result = [{'name': x[0], 'url': x[1], 'category_id' : x[2]} for x in self.cur.fetchall()]
        self._close()
        return result

    def save(self, name, url,category_id):
        self.destroy(url)
        self._connect()
        self.cur.execute('INSERT INTO channels(name,url,category_id) VALUES(?,?,?)', (name, url, category_id))
        self.db.commit()
        self._close()

    def destroy(self, url):
        self._connect()
        self.cur.execute('DELETE FROM channels WHERE url=?', (url, ))
        self.db.commit()
        self._close()

    def _connect(self):
        try:
          self.db = sqlite.connect(self.filename)
          self.db.text_factory = str
          self.cur = self.db.cursor()
        except:
          raise "*** Cann't connect to channels DB !!!"

    def _drop(self):
        self._connect()
        self.cur.execute('DROP TABLE IF EXISTS channels')
        self.db.commit()
        self._close()

    def _close(self):
        self.cur.close()
        self.db.close()
