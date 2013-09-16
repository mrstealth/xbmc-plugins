#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.0
# -*- coding: utf-8 -*-

import os
import sqlite3 as sqlite
from datetime import datetime

import xbmcaddon

__addon__ = xbmcaddon.Addon(id='plugin.video.unified.search')
addon_path = __addon__.getAddonInfo('path')

class ResultsDB:
    def __init__(self):
        self.filename = os.path.join(addon_path, 'resources/databases', 'search_results.sqlite')

        self._connect()
        self.cur.execute('pragma auto_vacuum=1')
        self.cur.execute("CREATE TABLE IF NOT EXISTS results (created_at TIMESTAMP, title TEXT, url TEXT, image TEXT, plugin TEXT)")
        self.db.commit()
        self._close()

    # def exists(self, title):
    #     self._connect()
    #     self.cur.execute("SELECT EXISTS(SELECT 1 FROM results WHERE title=? LIMIT 1)", (title, ))
    #     result = [x[0] for x in self.cur.fetchall()][0]
    #     self._close()

    #     return result

    # def find(self, title):
    #     self._connect()
    #     self.cur.execute("SELECT title, url, image, plugin,  created_at FROM results WHERE title=?", (title, ))
    #     result = [{'title': x[0], 'url': x[1], 'image': x[2], 'plugin': x[3], 'created_at' : x[4]} for x in self.cur.fetchall()]
    #     self._close()
    #     return result[0]

    # def last(self):
    #     self._connect()
    #     self.cur.execute("SELECT title, url, image, plugin,  created_at FROM results ORDER BY created_at DESC")
    #     result = [{'title': x[0], 'url': x[1], 'image': x[2], 'plugin': x[3], 'created_at' : x[4]} for x in self.cur.fetchall()]
    #     self._close()
    #     return result[0]

    def find_all(self):
        self._connect()
        self.cur.execute("SELECT title, url, image, plugin, created_at FROM results ORDER BY title ASC")

        results = [{'title': x[0], 'url': x[1], 'image': x[2], 'plugin': x[3], 'created_at' : x[4]} for x in self.cur.fetchall()]
        self._close()
        return results

    def save(self, title, url, image, plugin):
        self.destroy(title)
        self._connect()
        self.cur.execute('INSERT INTO results(title, url, image, plugin, created_at) VALUES(?,?,?,?,?)', ( title, url, image, plugin, datetime.today()))
        self.db.commit()
        self._close()

    def destroy(self, title):
        self._connect()
        self.cur.execute('DELETE FROM results WHERE title=?', (title, ))
        self.db.commit()
        self._close()

    def _connect(self):
        self.db = sqlite.connect(self.filename)
        self.db.text_factory = str
        self.cur = self.db.cursor()

    def drop(self):
        if os.path.isfile(self.filename):
            self._connect()
            self.cur.execute('DELETE FROM results')
            self.db.commit()

    def _close(self):
        self.cur.close()
        self.db.close()
