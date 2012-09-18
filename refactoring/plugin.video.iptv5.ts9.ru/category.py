#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.2
# -*- coding: utf-8 -*-

import os, time, xbmcaddon
import sqlite3 as sqlite

__addon__ = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')
addon_path = __addon__.getAddonInfo('path')

class Category:
    def __init__(self):
        self.filename = os.path.join(addon_path, 'resources', 'category.sqlite')

        self._connect()
        self.cur.execute('pragma auto_vacuum=1')
        self.cur.execute("CREATE TABLE IF NOT EXISTS categories (created_at integer, name TEXT, optgroupid TEXT)")
        self.cur.execute('CREATE INDEX IF NOT EXISTS time on categories(created_at desc)')
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

    def save(self, name, optgroupid):
        self.destroy(name)
        self._connect()
        self.cur.execute('INSERT INTO categories(created_at,name,optgroupid) VALUES(?,?,?)', (int(time.time()), name, optgroupid))
        self.db.commit()
        self._close()

    def destroy(self, name):
        self._connect()
        self.cur.execute('DELETE FROM categories WHERE name=?', (name, ))
        self.db.commit()
        self._close()

    def checkNeeded(self, optgroupid):
        self._connect()
        self.cur.execute("SELECT created_at FROM categories WHERE optgroupid=?", (optgroupid, ))
        created_at = int(self.cur.fetchall()[0][0])
        self._close()
        
        interval = int(__addon__.getSetting('interval'))*60*60
        now = int(time.time())
        created_at = created_at - interval
 
        if created_at+interval - now > 0:
            print "*** Skip stream availability check"
            return False
        else:
            print "*** Check stream availability"
            return True
            
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
