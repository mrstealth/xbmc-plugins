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

class Search:
    def __init__(self):
        self.filename = os.path.join(addon_path, 'resources/databases', 'searches.sqlite')
        self.connect()

    def connect(self):
        self.db = sqlite.connect(self.filename)
        self.db.text_factory = str
        self.cursor = self.db.cursor()

        self.execute = self.cursor.execute
        self.commit = self.db.commit()

        self.create_if_not_exists()

    def search_id(self):
        self.execute("SELECT MAX(id) FROM searches")
        counter = self.cursor.fetchone()[0]
        counter = counter + 1 if counter else 1
        return counter

    def save(self, keyword):
        self.execute('INSERT INTO searches(id, keyword) VALUES(?,?)', (self.search_id(), keyword))
        self.db.commit()

    def all(self):
        self.execute("SELECT * FROM searches")
        return [{'id': x[0], 'keyword': x[1]} for x in self.cursor.fetchall()]

    def create_if_not_exists(self):
        self.execute("CREATE TABLE IF NOT EXISTS searches (id INT, keyword TEXT)")
        self.db.commit()

    def drop(self):
        if os.path.isfile(self.filename):
            self.connect()
            self.execute('DELETE FROM searches')
            self.db.commit()

    def close(self):
        self.cursor.close()
        self.db.close()
