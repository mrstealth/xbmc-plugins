#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.5
# -*- coding: utf-8 -*-

import os
import urllib
import urllib2
import sys
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import XbmcHelpers
common = XbmcHelpers


import Translit as translit
translit = translit.Translit(encoding='cp1251')

sys.path.append(os.path.join(os.path.dirname(__file__), "../plugin.video.unified.search"))
from unified_search import UnifiedSearch


class Filmodrom():
    def __init__(self):
        self.id = 'plugin.video.filmodrom.net'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])
        self.url = 'http://filmodrom.net'

        self.inext = os.path.join(self.path, 'resources/icons/next.png')
        self.isearch = os.path.join(self.path, 'resources/icons/search.png')
        self.ifolder = os.path.join(self.path, 'resources/icons/folder.png')

        self.debug = self.addon.getSetting("debug") == 'true'

    def main(self):
        params = common.getParameters(sys.argv[2])
        mode = url = page = None
        title = image = genre = desc = None

        mode = params['mode'] if 'mode' in params else None
        url = urllib.unquote_plus(params['url']) if 'url' in params else None
        page = params['page'] if 'page' in params else 1

        keyword = params['keyword'] if 'keyword' in params else None
        unified = params['unified'] if 'unified' in params else None

        if mode == 'play':
            self.playItem(url)
        if mode == 'search':
            self.search(keyword, unified)
        if mode == 'genres':
            self.listGenres(url)
        if mode == 'show':
            self.show(url, title, image, genre, desc)
        if mode == 'category':
            self.getCategoryItems(url, page)
        elif mode is None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FF00][%s][/COLOR]" % self.language(2000), iconImage=self.isearch)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("genres", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(1000), iconImage=self.ifolder)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        # uri = sys.argv[0] + '?mode=%s&url=%s' % ("category", "http://filmodrom.net/otechestvennue/")
        # item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(1001), iconImage=self.ifolder)
        # xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        # uri = sys.argv[0] + '?mode=%s&url=%s' % ("category", "http://filmodrom.net/serial/")
        # item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(1002), iconImage=self.ifolder)
        # xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        # uri = sys.argv[0] + '?mode=%s&url=%s' % ("category", "http://filmodrom.net/multfilms/")
        # item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(1003), iconImage=self.ifolder)
        # xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.getCategoryItems(self.url, 1)

        xbmcplugin.endOfDirectory(self.handle, True)

    def getCategoryItems(self, url, page):
        self.log("*** Get category items %s" % url)

        page_url = "%s/page/%s/" % (url, str(int(page)))
        response = common.fetchPage({"link": page_url})
        items = 0

        if response["status"] == 200:
            content = common.parseDOM(response["content"], "div", attrs={"id": "dle-content"})
            movie = common.parseDOM(content, "div", attrs={"class": "notes"})

            header = common.parseDOM(movie, "h4")
            links = common.parseDOM(header, "a", ret="href")
            titles = common.parseDOM(header, "a")

            image_container = common.parseDOM(movie, "td", attrs={"valign": "top"})
            images = common.parseDOM(image_container, "img", ret="src")

            genres_container = common.parseDOM(movie, "div", attrs={"style": "background: #323232; padding: 0px 5px 0px 5px;"})
            genres = common.parseDOM(genres_container, "a")

            descriptions = common.parseDOM(movie, "div", attrs={"style": "display:inline;"})
            pagenav = common.parseDOM(content, "div", attrs={"class": "ctitl"})

            ratings = common.parseDOM(movie, "li", attrs={"class": "current-rating"})

            for i, title in enumerate(titles):
                items += 1

                title = self.encode(title)
                genre = self.encode(genres[i])
                desc = self.encode(descriptions[i])

                infoLabels = {'title': title, 'genre': genre, 'plot': desc}

                if self.calculateRating(ratings[i]) > 0:
                    infoLabels['rating'] = self.calculateRating(ratings[i])

                uri = sys.argv[0] + '?mode=show&url=%s' % links[i]
                item = xbmcgui.ListItem(title, thumbnailImage=self.url + images[i])
                item.setInfo(type='Video', infoLabels=infoLabels)
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status%s" % response["status"])

        if pagenav and not items < 10:
            uri = sys.argv[0] + '?mode=%s&url=%s&page=%s' % ("category", url, str(int(page) + 1))
            item = xbmcgui.ListItem(self.language(9001), iconImage=self.inext)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def show(self, url, title, image, genre, desc):
        self.log("*** Show for %s" % url)

        response = common.fetchPage({"link": url})

        if response["status"] == 200:
            content = common.parseDOM(response["content"], "div", attrs={"id": "dle-content"})
            movie = common.parseDOM(content, "div", attrs={"class": "notes"})
            title = common.parseDOM(movie, "h4")

            image_container = common.parseDOM(movie, "td", attrs={"valign": "top"})
            image = common.parseDOM(image_container, "img", ret="src")

            description = common.parseDOM(movie, "div", attrs={"style": "display:inline;"})

            flash = common.parseDOM(content, 'object')

            season = common.parseDOM(flash, "param", attrs={"name": "flashvars"})
            movie = common.parseDOM(flash, "param", attrs={"name": "flashvars"}, ret="file")

            if movie:
                self.log("This is a film %s " % movie)

                title = self.encode(title[0])
                desc = self.encode(description[0])

                item = xbmcgui.ListItem(title, thumbnailImage=self.url + image[0])
                item.setInfo(type='Video', infoLabels={'title': title, 'genre': 'N/A', 'plot': desc})
                item.setProperty('IsPlayable', 'true')

                uri = sys.argv[0] + '?mode=play&url=%s' % urllib.quote_plus(movie[-1].replace('"', ''))
                xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
                xbmc.executebuiltin('Container.SetViewMode(52)')

            else:
                self.log("This is a season %s" % season)

                url = season[0].split('&amp;pl=')[-1].split('"')[0]
                response = common.fetchPage({"link": url})
                response = eval(response["content"])

                if 'playlist' in response['playlist'][0]:
                    self.log("This is a season multiple seasons")

                    for season in response['playlist']:
                        episods = season['playlist']

                        for episode in episods:
                            etitle = "%s (%s)" % (episode['comment'], common.stripTags(season['comment']))
                            url = episode['file']

                            uri = sys.argv[0] + '?mode=play&url=%s' % url
                            item = xbmcgui.ListItem(etitle, thumbnailImage=self.url + image[0])

                            item.setInfo(type='Video', infoLabels={
                                'title': title,
                                'plot': desc,
                                'overlay': xbmcgui.ICON_OVERLAY_WATCHED,
                                'playCount': 0
                            })
                            item.setProperty('IsPlayable', 'true')
                            xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

                else:
                    self.log("This is one season")
                    for episode in response['playlist']:
                        etitle = episode['comment']
                        url = episode['file']

                        uri = sys.argv[0] + '?mode=play&url=%s' % url
                        item = xbmcgui.ListItem(etitle, thumbnailImage=self.url + image[0])

                        item.setInfo(type='Video', infoLabels={'title': title, 'plot': desc, 'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0})
                        item.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

                xbmc.executebuiltin('Container.SetViewMode(51)')

        else:
            self.showErrorMessage("getFilmInfo(): Bad response status%s" % response["status"])

        xbmcplugin.endOfDirectory(self.handle, True)

    def listGenres(self, url):
        self.log("list genres")

        response = common.fetchPage({"link": url})
        genres = common.parseDOM(response["content"], "ul", attrs={"class": "mainmenu accordion"})

        titles = common.parseDOM(genres, "a")[:-3]
        links = common.parseDOM(genres, "a", ret="href")[:-3]

        for i, title in enumerate(titles):
            uri = sys.argv[0] + '?mode=category&url=%s' % self.url + links[i]
            item = xbmcgui.ListItem(self.encode(title), thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmcplugin.endOfDirectory(self.handle, True)

    def playItem(self, url):
        self.log("*** play url %s" % url)
        item = xbmcgui.ListItem(path=url)
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
            self.log("You are looking for: %s" % keyword.decode('cp1251').encode('utf-8'))

            # Simple search
            # values = {
            #     "do":           "search",
            #     "story":        keyword,
            #     "subaction":    "search",
            #     "x":            0,
            #     "y":            0
            # }

            # headers = {
            #     "Host" : "filmodrom.net",
            #     "Referer" : 'http://filmodrom.net/index.php',
            #     "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0"
            # }

            # request = urllib2.Request(url, urllib.urlencode(values), headers)
            # response = urllib2.urlopen(request)

            # Advanced search: titles only
            url = 'http://filmodrom.net/index.php?do=search'

            headers = {
                "Host" : "filmodrom.net",
                "Referer" : 'http://filmodrom.net/index.php',
                "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0"
            }

            values = {
                "beforeafter":      "after",
                "catlist[]":        "0",
                "do":               "search",
                "full_search":      "1",
                "replyless":        "0",
                "replylimit":       "0",
                "resorder":         "desc",
                "result_from":      "1",
                "result_num":       "20",
                "search_start":     "1",
                "searchdate":       "0",
                "searchuser":       "",
                "showposts":        "0",
                "sortby":           "date",
                "story":            keyword,
                "subaction":        "search",
                "titleonly":        3
            }

            request = urllib2.Request(url, urllib.urlencode(values), headers)
            # request = urllib2.Request(url, urllib.urlencode(values))
            response = urllib2.urlopen(request)

            content = common.parseDOM(response.read(), "div", attrs={"id": "dle-content"})
            table = common.parseDOM(content, "table")

            header = common.parseDOM(table, "strong")
            links = common.parseDOM(header, "a", ret="href")
            titles = common.parseDOM(header, "a")

            if titles:
                if unified:
                    self.log("Perform unified search and return results")

                    for i, title in enumerate(titles):
                        unified_search_results.append({'title': self.encode(title), 'url': links[i], 'image': None, 'plugin': self.id})
                else:
                    for i, title in enumerate(titles):
                        uri = sys.argv[0] + '?mode=show&url=%s' % links[i]
                        item = xbmcgui.ListItem(self.encode(title), iconImage=self.icon, thumbnailImage=self.icon)
                        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
            else:
                item = xbmcgui.ListItem(self.language(2001).encode('utf-8'), iconImage=self.icon, thumbnailImage=self.icon)
                xbmcplugin.addDirectoryItem(self.handle, '', item, True)

            UnifiedSearch().collect(unified_search_results)

        else:
            self.menu()

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def log(self, message):
        if self.debug:
            print "=== %s: %s" % (self.id, message)

    def error(self, message):
        print "%s ERROR: %s" % (self.id, message)

    def calculateRating(self, x):
        rating = (int(x)*100)/85
        xbmc_rating = (rating*10)/100
        return xbmc_rating

    def showErrorMessage(self, msg):
        print msg
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("ERROR", msg, str(10 * 1000)))

    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')

plugin = Filmodrom()
plugin.main()
