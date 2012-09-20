#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.6
# -*- coding: utf-8 -*-


import os, time, xbmcaddon
import sqlite3 as sqlite

__addon__ = xbmcaddon.Addon(id='plugin.video.iptv.root-host.pro')
addon_path = __addon__.getAddonInfo('path')

class Channel:
    def __init__(self):
        self.filename = os.path.join(addon_path, 'resources', 'channel.sqlite')

        self._connect()
        self.cur.execute('pragma auto_vacuum=1')
        self.cur.execute("CREATE TABLE IF NOT EXISTS channels (image TEXT, url TEXT, name TEXT, category TEXT)")
        self.db.commit()
        self._close()

#     def find(self, url):
#         self._connect()
#         self.cur.execute("SELECT image, name, url, category FROM channels WHERE url=?", (url, ))
#         result = [x[0], x[1], x[2], x[3] for x in self.cur.fetchall()
#         self._close()
# 
#         return result

    def exists(self, url):
        self._connect()
        self.cur.execute("SELECT EXISTS(SELECT 1 FROM channels WHERE url=? LIMIT 1)", (url, ))
        result = [x[0] for x in self.cur.fetchall()][0]
        self._close()
        return result

    def find_by_category_name(self, category):
        self._connect()
        self.cur.execute("SELECT image, url, name, category FROM channels WHERE category=? ORDER BY name ASC", (category, ))
        result = [[x[0],x[1],x[2],x[3]] for x in self.cur.fetchall()]
        self._close()
        return result

    def get_categories(self):
        self._connect()
        self.cur.execute("SELECT category FROM channels GROUP BY category ORDER BY category ASC")
        result = [x[0] for x in self.cur.fetchall()]
        self._close()
        return result
        
    def save(self, image, name, url, category):
        self.destroy(url)
        self._connect()
        self.cur.execute('INSERT INTO channels(image, url,name,category) VALUES(?,?,?,?)', (image,url,name,category))
        self.db.commit()
        self._close()

    def destroy(self, url):
        self._connect()
        self.cur.execute('DELETE FROM channels WHERE url=?', (url, ))
        self.db.commit()
        self._close()

    def favorites(self):
        self._connect()
        self.cur.execute("SELECT image,name, url FROM channels WHERE is_fav=1 ORDER BY name ASC")
        result = [{x[0] : x[1]} for x in self.cur.fetchall()]
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

    def _drop(self):
        self._connect()
        self.cur.execute('DROP TABLE IF EXISTS channels')
        self.db.commit()
        self._close()

    def _close(self):
        self.cur.close()
        self.db.close()
