#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.1.3
# -*- coding: utf-8 -*-

import os
import sys
import urllib
import urllib2
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon

import XbmcHelpers
common = XbmcHelpers

import Translit as translit
translit = translit.Translit()

# Import UnifiedSearch
sys.path.append(os.path.dirname(__file__)+ '/../plugin.video.unified.search')
from unified_search import UnifiedSearch

class Kinosolo():
    def __init__(self):
        self.id = 'plugin.video.kinosolo.ru'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString

        self.handle = int(sys.argv[1])
        self.params = sys.argv[2]

        self.url = 'http://kinosolo.ru'

        self.inext = os.path.join(self.path, 'resources/icons/next.png')
        self.debug = False

    def main(self):
        self.log("Addon: %s"  % self.id)
        self.log("Handle: %d" % self.handle)
        self.log("Params: %s" % self.params)

        params = common.getParameters(self.params)
        mode = url = page = category = None

        mode = params['mode'] if 'mode' in params else None
        url = urllib.unquote_plus(params['url']) if 'url' in params else None
        page = params['page'] if 'page'in params else 1
        category = params['category'] if 'category'in params else 'main'

        keyword = params['keyword'] if 'keyword' in params else None
        unified = params['unified'] if 'unified' in params else None

        if mode == 'play':
            self.playItem(url)
        if mode == 'search':
            self.search(keyword, unified)
        if mode == 'genres':
            self.listGenres(url)
        if mode == 'show':
            self.getMovieInfo(url)
        if mode == 'category':
            self.getMovies(url, category, page)
        elif mode == None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FF00][%s][/COLOR]" % self.language(2000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("genres", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(1000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.getMovies(self.url, 'main', '1')

        xbmcplugin.endOfDirectory(self.handle, True)

    def getMovies(self, url, category, page):
        if category == 'main':
            page_url = "%s/load/0-%s" % (url, page)
        else:
            page_url = "%s-%s-%s" % (url, str(page), '13')

        response = common.fetchPage({"link": page_url})
        items = 0

        if response["status"] == 200:
            container = common.parseDOM(response["content"], "div", attrs={"id": "allEntries"})
            movie = common.parseDOM(container, "div", attrs={"class": "post"})

            movie_header = common.parseDOM(movie, "div", attrs={"class": "post-title"})
            movie_body = common.parseDOM(movie, "div", attrs={"class": "post-story"})
            movie_footer = common.parseDOM(movie, "div", attrs={"class": "post-data"})

            titles = common.parseDOM(movie_header, "a")
            links = common.parseDOM(movie_header, "a", ret="href")
            images = common.parseDOM(movie_body, "img", ret="src")

            for i, title in enumerate(titles):
                items += 1

                infos = common.parseDOM(movie_body[i], "td")[0].split('</b>')
                year = infos[1].split('<br>')[0].replace('-', '').replace(' ', '')
                genre = common.parseDOM(movie_footer[i], "a")[0]

                title = "%s (%s)" % (title.replace(self.language(5002), ''), year)
                desc = common.stripTags(infos[-1].encode('utf-8')).replace('- ', '').replace(' -', '').replace('&nbsp;', '')

                uri = sys.argv[0] + '?mode=show&url=%s' % links[i]
                item = xbmcgui.ListItem(title, thumbnailImage=images[i])
                item.setInfo(type='Video', infoLabels={"title": title, "genre": genre, "plot": desc})
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status%s" % response["status"])

        if not items < 10:
            if category == 'main':
                uri = sys.argv[0] + '?mode=%s&url=%s&category=%s&page=%s' % ("category", url, 'main', str(int(page) + 1))
            else:
                uri = sys.argv[0] + '?mode=%s&url=%s&category=%s&page=%s' % ("category", url, 'genre', str(int(page) + 1))

            item = xbmcgui.ListItem(self.language(9001), thumbnailImage=self.inext)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def getMovieInfo(self, url):
        response = common.fetchPage({"link": url})

        if response["status"] == 200:

            content = common.parseDOM(response["content"], "div", attrs={"id": "content"})
            movie_header = common.parseDOM(content, "div", attrs={"class": "post-title"})
            movie_body = common.parseDOM(content, "div", attrs={"class": "post-story"})

            title = common.parseDOM(movie_header, "a")[0]
            image = common.parseDOM(movie_body, "img", ret="src")[0]

            iframe = common.parseDOM(content, "iframe", ret="src")[0]
            content = self.getIframeContent(iframe, url)
            link = common.parseDOM(content, "param", attrs={"name": "flashvars"}, ret="file")[0][:-1]

            item = xbmcgui.ListItem(title, thumbnailImage=image)
            item.setProperty('IsPlayable', 'true')

            uri = sys.argv[0] + '?mode=play&url=%s' % link
            xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        else:
            self.showErrorMessage("getMovieInfo(): Bad response status%s" % response["status"])

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def listGenres(self, url):
        response = common.fetchPage({"link": url})

        container = common.parseDOM(response["content"], "div", attrs={"id": "right"})
        genres = common.parseDOM(container, "ul", attrs={"class": "menu"})

        titles = common.parseDOM(genres, "a")
        links = common.parseDOM(genres, "a", ret="href")

        for i, title in enumerate(titles):
            uri = sys.argv[0] + '?mode=category&url=%s&category=genre&page=1' % links[i]
            item = xbmcgui.ListItem(title, thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmcplugin.endOfDirectory(self.handle, True)

    def getIframeContent(self, url, referer):
        from time import time

        timestamp = str(int(time()))
        request = urllib2.Request(url)
        request.add_header("Cookie", "ekinopanoramauzll=%s" % timestamp)
        request.add_header("Host", "onlainfilm.ucoz.ua.sv1.kinosolo.ru")
        request.add_header("Referer", referer)
        request.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64; rv:18.0) Gecko/20100101 Firefox/18.0")

        response = urllib2.urlopen(request)
        return response.read()

    def playItem(self, url):
        print "Play URL %s" % url

        if '+or+' in url  or ' or ' in url:
            self.log("Wrong URL format: %s" % url)
            video_url =  url.split('+or+')[-1]
        else:
            video_url = url

        item = xbmcgui.ListItem(path=video_url)
        xbmcplugin.setResolvedUrl(self.handle, True, item)

    def getUserInput(self):
        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        kbd.setHeading(self.language(4000))
        kbd.doModal()
        keyword = None

        if kbd.isConfirmed():
            if self.addon.getSetting('translit') == 'true':
                keyword = translit.rus(kbd.getText())
            else:
                keyword = kbd.getText()
        return keyword

    def search(self, keyword, unified):
        keyword = translit.rus(keyword) if unified else self.getUserInput()
        unified_search_results = []

        if keyword:
            search_url = "http://kinosolo.ru/load/"

            # Advanced search: titles only
            values = {
                "a":  2,
                "do.x":  0,
                "do.y" :  0,
                "query": keyword,
            }

            # Send request to server
            request = urllib2.Request(search_url, urllib.urlencode(values))
            response = urllib2.urlopen(request)

            movie = common.parseDOM(response.read(), "div", attrs={"class": "post"})

            movie_header = common.parseDOM(movie, "div", attrs={"class": "post-title"})
            movie_body = common.parseDOM(movie, "div", attrs={"class": "post-story"})
            movie_footer = common.parseDOM(movie, "div", attrs={"class": "post-data"})

            titles = common.parseDOM(movie_header, "a")
            links = common.parseDOM(movie_header, "a", ret="href")
            images = common.parseDOM(movie_body, "img", ret="src")

            if unified:
                self.log("Perform unified search and return results")

                for i, title in enumerate(titles):
                    title = title.replace(self.language(5002), '')
                    unified_search_results.append({'title':  title, 'url': links[i], 'image': images[i], 'plugin': self.id})

                UnifiedSearch().collect(unified_search_results)

            else:
                for i, title in enumerate(titles):
                    title = title.replace(self.language(5002), '')

                    uri = sys.argv[0] + '?mode=show&url=%s' % links[i]
                    item = xbmcgui.ListItem(title, thumbnailImage=images[i])
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

                xbmc.executebuiltin('Container.SetViewMode(50)')
                xbmcplugin.endOfDirectory(self.handle, True)

        else:
            self.menu()

    # XBMC helpers
    def showErrorMessage(self, msg):
        print msg
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("ERROR", msg, str(10 * 1000)))

    # Python helpers
    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')

    # Addon helpers
    def log(self, message):
        if self.debug:
            print "### %s: %s" % (self.id, message)

    def error(self, message):
        print "%s ERROR: %s" % (self.id, message)

    def isCyrillic(self, keyword):
        if not re.findall(u"[\u0400-\u0500]+", keyword):
            return False
        else:
            return True

plugin = Kinosolo()
plugin.main()
