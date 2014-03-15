#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.3
# -*- coding: utf-8 -*-

import os
import sys

import urllib
import urllib2

import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon

import uppod

import XbmcHelpers
common = XbmcHelpers


import Translit as translit
translit = translit.Translit(encoding='cp1251')

sys.path.append(os.path.dirname(__file__)+ '/../plugin.video.unified.search')
from unified_search import UnifiedSearch


class Fepcom():
    def __init__(self):
        self.id = 'plugin.video.mrstealth.fepcom.net'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])
        self.url = 'http://fepcom.net'

        self.inext = os.path.join(self.path, 'resources/icons/next.png')

        self.debug = self.addon.getSetting("debug") == 'true'

    def main(self):
        params = common.getParameters(sys.argv[2])
        mode = url = page = None

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
        if mode == 'alphabet':
            self.listAlphabet()
        if mode == 'show':
            self.getFilmInfo(url)
        if mode == 'category':
            self.getCategoryItems(url, page)
        if mode == 'unformatted_category':
            self.simpleItemListing(url, page)
        elif mode is None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FF00][%s][/COLOR]" % self.language(2000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("genres", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(1000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("alphabet", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(1001), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.getCategoryItems('http://fepcom.net/filmy-onlajn/', 1)
        xbmcplugin.endOfDirectory(self.handle, True)

    def getCategoryItems(self, url, page):
        print "*** Get category items %s" % url

        page_url = url if page == 0 else "%spage/%s/" % (url, str(int(page)))
        response = common.fetchPage({"link": page_url})

        print page_url

        if response["status"] == 200:
            container = common.parseDOM(response["content"], "div", attrs={"id": "col_content"})
            posts = common.parseDOM(container, "div", attrs={"class": "short_post"})
            navigation = common.parseDOM(container, "div", attrs={"class": "navigation"})
            items = 0

            for i, post in enumerate(posts):
                items += 1

                post_link = common.parseDOM(post, "div", attrs={"class": "short_post_link"})
                post_image = common.parseDOM(post, "div", attrs={"class": "short_post_img2"})
                short_post_text = self.encode(common.parseDOM(post_image, "div", attrs={"class": "short_post_text"})[0])

                links = common.parseDOM(post_link, "a")

                title = "%s (%s)" % (self.encode(links[0]), links[1])
                link = common.parseDOM(post_link, "a", ret="href")
                image = common.parseDOM(post_image, "img", ret="src")[0]

                ratings = common.parseDOM(post, 'div', attrs={"id": "ratig-layer"})
                rating = "%s : %s" % (self.language(6003), common.stripTags(common.parseDOM(ratings, 'b')[0]))

                try:
                    uri = sys.argv[0] + '?mode=show&url=%s' % link[0]
                    item = xbmcgui.ListItem(title, thumbnailImage=self.url + image)
                    item.setInfo(type='Video', infoLabels={'title': title, 'genre': rating, 'plot': short_post_text, 'rating': 0})
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

                except IndexError: 
                    print "IndexError"

            if navigation and not items < 40:
                uri = sys.argv[0] + '?mode=%s&url=%s&page=%s' % ("category", url, str(int(page) + 1))
                item = xbmcgui.ListItem(self.language(9001), iconImage=self.inext)
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status%s" % response["status"])

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def simpleItemListing(self, url, page):
        page_url = url if page == 0 else "%spage/%s/" % (url, str(int(page)))
        response = common.fetchPage({"link": page_url})

        print "*** Get category items %s" % page_url

        if response["status"] == 200:
            container = common.parseDOM(response["content"], "div", attrs={"id": "dle-content"})
            posts = common.parseDOM(container, "li")
            navigation = common.parseDOM(container, "div", attrs={"class": "navigation"})
            items = 0

            print len(posts)
            for i, post in enumerate(posts):
                items += 1

                titles = common.parseDOM(post, "a")
                links = common.parseDOM(post, "a", ret="href")
                genre =','.join(titles[1:])
                short_post_text = self.encode(common.parseDOM(post, "div", attrs={"class" : "short_post_text"})[0])

                uri = sys.argv[0] + '?mode=show&url=%s' % links[0]
                item = xbmcgui.ListItem(self.encode(titles[0]), thumbnailImage=self.icon)
                item.setInfo(type='Video', infoLabels={'title': self.encode(titles[0]), 'genre': genre, 'plot': short_post_text, 'rating': 0})
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

            if navigation and not items < 100:
                uri = sys.argv[0] + '?mode=%s&url=%s&page=%s' % ("unformatted_category", url, str(int(page) + 1))
                item = xbmcgui.ListItem(self.language(9001), iconImage=self.inext)
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status%s" % response["status"])

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)      

    def getFilmInfo(self, url):
        print "*** getFilmInfo %s" % url
        
        response = common.fetchPage({"link": url})

        content = common.parseDOM(response["content"], "div", attrs={"id": "dle-content"})
        post = common.parseDOM(content, "div", attrs={"class": "post"})

        post_content = common.parseDOM(content, "div", attrs={"class": "post_content"})

        title = self.encode(common.parseDOM(post, "h1")[0])
        image = common.parseDOM(post_content, "img", ret="src")[0]

        videos = common.parseDOM(post, "div", attrs={"class": "video"})
        players = common.parseDOM(videos, "object")

        for i, player in enumerate(players):
            uhash = common.parseDOM(player, "param", attrs={"name": "flashvars"}, ret="file")[0].split('&')[0]

            # get encoded URL from playlist/file HASH
            uppod_url = uppod.decodeSourceURL(uhash)
            image = image if 'http' in image else self.url+image

            uri = sys.argv[0] + '?mode=play&url=%s' % uppod_url
            info = {'title': title, 'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0}
            
            if len(players) > 1:
                item = xbmcgui.ListItem("%s (source %i)" % (title, i+1), thumbnailImage=image)
            else: 
                 item = xbmcgui.ListItem("%s" % title, thumbnailImage=image)

            item.setInfo(type='Video', infoLabels=info)
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def listGenres(self, url):
        print "list genres"
        response = common.fetchPage({"link": url})
        container = common.parseDOM(response["content"], "div", attrs={"id": "col_left"})
        ul = common.parseDOM(container, "ul")
        titles = common.parseDOM(ul[0], "a")
        links = common.parseDOM(ul[0], "a", ret="href")

        for i, title in enumerate(titles):
            link = links[i] if links[i].startswith('http') else self.url + links[i]
            uri = sys.argv[0] + '?mode=category&url=%s' % link
            item = xbmcgui.ListItem(self.encode(title), thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmcplugin.endOfDirectory(self.handle, True)

    def listAlphabet(self):
        response = common.fetchPage({"link": self.url})
        container = common.parseDOM(response["content"], "div", attrs={"id": "catalogue_az"})
        ul = common.parseDOM(container, "ul")
        titles = common.parseDOM(ul[0], "a")
        links = common.parseDOM(ul[0], "a", ret="href")

        for i, title in enumerate(titles):
            link = links[i] if links[i].startswith('http') else self.url + links[i]
            uri = sys.argv[0] + '?mode=unformatted_category&url=%s' % link
            item = xbmcgui.ListItem(self.encode(title), thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmcplugin.endOfDirectory(self.handle, True)

    def playItem(self, url):
        print "*** play url %s" % url
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
        self.log("*** Search: unified %s" % unified)
        
        keyword = translit.rus(keyword) if unified else self.getUserInput()
        unified_search_results = []

        if keyword:
            url = 'http://fepcom.net/index.php?do=search'

            # Advanced search: titles only
            values = {
                "beforeafter":  "after",
                "catlist[]":    30,
                "do" :          "search",
                "full_search":  1,
                "replyless":    0,
                "replylimit":   0,
                "resorder":     "desc",
                "result_from":  1,
                "search_start": 1,
                "searchdate" :  0,
                "searchuser":   "",
                "showposts":    0,
                "sortby":       "date",
                "story" :       keyword,
                "subaction":    "search",
                "titleonly":    "3"
            }
           
            headers = {
                "Host" : "fepcom.net",
                "Referer" : 'http://fepcom.net/index.php?do=search',
                "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:23.0) Gecko/20100101 Firefox/23.0"
            }

            # Send request to server
            request = urllib2.Request(url, urllib.urlencode(values), headers)
            response = urllib2.urlopen(request)
            content = response.read()

            posts = common.parseDOM(content, "div", attrs={"class": "post"})
            headers = common.parseDOM(content, "h2")

            titles = common.parseDOM(headers, "a")
            links = common.parseDOM(headers, "a",  ret="href")
            images = common.parseDOM(posts, "img",  ret="src")

            if unified:
                self.log("Perform unified search and return results")

                for i, title in enumerate(titles):
                    unified_search_results.append({'title':  self.encode(title), 'url': links[i], 'image': self.url + images[i], 'plugin': self.id})

                UnifiedSearch().collect(unified_search_results)

            else:
                for i, title in enumerate(titles):
                    uri = sys.argv[0] + '?mode=show&url=%s' % links[i]
                    item = xbmcgui.ListItem(self.encode(title), thumbnailImage=self.url + images[i])
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

                xbmc.executebuiltin('Container.SetViewMode(50)')
                xbmcplugin.endOfDirectory(self.handle, True)

        else:
            self.menu()

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

    def showErrorMessage(self, msg):
        print msg
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("ERROR", msg, str(10 * 1000)))

    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')

plugin = Fepcom()
plugin.main()
