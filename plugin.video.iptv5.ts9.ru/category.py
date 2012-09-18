import sqlite3 as sqlite
import time, os, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')
addon_icon    = Addon.getAddonInfo('icon')
addon_path    = Addon.getAddonInfo('path')
__settings__ = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')

class Category:
    def __init__(self, filename):
        self.filename = os.path.join(addon_path, 'resources', 'category.sqlite')

        self._connect()
        self.cur.execute('pragma auto_vacuum=1')
        self.cur.execute("CREATE TABLE IF NOT EXISTS categories (created_at integer, name TEXT, channels TEXT)")
        self.cur.execute('CREATE INDEX IF NOT EXISTS time on categories(created_at desc)')
        self.db.commit()
        self._close()
        #else:
        #    print "Database file is not exists, create one"

    def get(self, name):
        #print "**** Get name " + name
        self._connect()
        self.cur.execute("SELECT name, channels, created_at FROM categories WHERE name=?", (name, ))
        res = [{'name': x[0], 'channels': x[1], 'created_at' : x[2]} for x in self.cur.fetchall()]
        self._close()
        return res[0]

    def all(self):
        self._connect()
        self.cur.execute("SELECT name,created_at FROM categories ORDER BY name ASC")
        res = [ x[0] for x in self.cur.fetchall()]
        self._close()
        return res

    def add(self, name, channels):
        #print "**** ADD name " + name
        self.delete(name)
        self._connect()
        self.cur.execute('INSERT INTO categories(created_at,name,channels) VALUES(?,?,?)', (int(time.time()), name, channels))
        self.db.commit()
        self._close()

    def delete(self, name):
        self._connect()
        self.cur.execute('DELETE FROM categories WHERE name=?', (name, ))
        self.db.commit()
        self._close()

    def _connect(self):
        self.db = sqlite.connect(self.filename)
        self.db.text_factory = str
        self.cur = self.db.cursor()

    def _drop(self):
        print "*** DROP TABLE categories"
        self._connect()
        self.cur.execute('DROP TABLE IF EXISTS categories')
        self.db.commit()
        self._close()

    def _close(self):
        self.cur.close()
        self.db.close()
