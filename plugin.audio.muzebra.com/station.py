#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.6
# -*- coding: utf-8 -*-


import os, datetime, xbmcaddon
import sqlite3 as sqlite
from datetime import timedelta

__addon__ = xbmcaddon.Addon(id='plugin.audio.muzebra.com')
addon_path = __addon__.getAddonInfo('path')

now = datetime.datetime.today()
if int(__addon__.getSetting('interval')) > 0:
    past = now - datetime.timedelta(hours=int(__addon__.getSetting('interval')))
else:
    past = now - datetime.timedelta(seconds=10)

class Station:
    def __init__(self):
        self.filename = os.path.join(addon_path, 'resources', 'stations.sqlite')

        self._connect()
        self.cur.execute('pragma auto_vacuum=1')
        self.cur.execute("CREATE TABLE IF NOT EXISTS stations (created_at TIMESTAMP, name TEXT, url TEXT, fav BOOLEAN DEFAULT '0' NOT NULL)")
        self.db.commit()
        self._close()

    def exists(self, url):
        self._connect()
        self.cur.execute("SELECT EXISTS(SELECT 1 FROM stations WHERE url=? LIMIT 1)", (url, ))
        result = [x[0] for x in self.cur.fetchall()][0]
        self._close()
        return result

    def find_all(self):
        self._connect()
        self.cur.execute("SELECT name,url FROM stations ORDER BY name")
        result = [{x[0]:x[1]} for x in self.cur.fetchall()]
        self._close()
        print result
        return result

    def save(self,name,url):
        self.destroy(url)
        self._connect()
        self.cur.execute('INSERT INTO stations(name,url,created_at) VALUES(?,?,?)', (name,url,now))
        self.db.commit()
        self._close()

    def destroy(self, url):
        self._connect()
        self.cur.execute('DELETE FROM stations WHERE url=?', (url, ))
        self.db.commit()
        self._close()

    def recheck(self):
        self._connect()
        self.cur.execute("SELECT created_at FROM stations WHERE created_at <=?", (past, ))
        result = [x[0] for x in self.cur.fetchall()]
        self._close()

        return True if result else False

    def favorites(self):
        self._connect()
        self.cur.execute("SELECT name,url FROM stations WHERE fav=1 ORDER BY name")
        result = [[x[0],x[1]] for x in self.cur.fetchall()]
        self._close()
        print result
        return result

    def addToFav(self, url):
        self._connect()
        self.cur.execute('UPDATE stations SET fav=1 WHERE url=?', (url, ))
        self.db.commit()
        self._close()

    def removeFromFav(self, url):
        self._connect()
        self.cur.execute('UPDATE channels SET fav=0 WHERE url=?', (url, ))
        self.db.commit()
        self._close()

    def drop(self):
        self._connect()
        self.cur.execute('DROP TABLE IF EXISTS stations')
        self.db.commit()
        self._close()

    def _connect(self):
        try:
          self.db = sqlite.connect(self.filename)
          self.db.text_factory = str
          self.cur = self.db.cursor()
        except:
          raise "*** Cann't connect to channels DB !!!"

    def _close(self):
        self.cur.close()
        self.db.close()
