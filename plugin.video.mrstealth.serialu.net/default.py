#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.9
# -*- coding: utf-8 -*-


import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon

import os
import urllib
import urllib2
import sys
import json
import uppod
import cookielib

import HTMLParser

import XbmcHelpers
common = XbmcHelpers

import Translit as translit
translit = translit.Translit(encoding='utf-8')

# My Favorites module
from MyFavorites import MyFavorites

class SerialuNet():
    def __init__(self):
        self.id = 'plugin.video.mrstealth.serialu.net'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])
        self.url = 'http://serialu.net'

        self.favorites = MyFavorites(self.id)
        self.inext = os.path.join(self.path, 'resources/icons/next.png')

    def main(self):
        params = common.getParameters(sys.argv[2])
        mode = url = page = None

        mode = params['mode'] if 'mode' in params else None
        url = urllib.unquote_plus(params['url']) if 'url' in params else None
        page = params['page'] if 'page' in params else 1

        if mode == 'play':
            self.playItem(url)
        if mode == 'search':
            self.search()
        if mode == 'genres':
            self.listGenres(url)
        if mode == 'show':
            self.getFilmInfo(url)
        if mode == 'category':
            self.getCategoryItems(url, page)
        if mode == 'favorites':
            self.show_favorites()
        elif mode is None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        item = xbmcgui.ListItem("[B][COLOR=FF00FF00]%s[/COLOR][/B]" % self.language(2000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.favorites.ListItem()

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("genres", self.url)
        item = xbmcgui.ListItem("[B][COLOR=FF00FFF0]%s[/COLOR][/B]" % self.language(1000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.getCategoryItems(self.url, 1)
        xbmcplugin.endOfDirectory(self.handle, True)

    def getCategoryItems(self, url, page):
        print "*** Get category items for page: %s and url: %s" % (page, url)

        # Search workaround
        if '?s=' in url:
            tmp = url.split('?s=')
            if page == 1:
                page_url = "%s/page/%s/?s=%s" % (self.url, str(int(page)), tmp[1])
            else:
                page_url = "%s/page/%s/?s=%s" % (self.url, str(int(page)), urllib.quote(tmp[1]))
        else:
            print "No search in url"
            if page == 1:
                page_url = url
            else:
                page_url = "%s/page/%s/" % (url, str(int(page)))

        print "Page URL: %s" % page_url

        response = self.get(page_url)
        items = 0

        if response:
            container = common.parseDOM(response, "div", attrs={"id": "column"})
            posts = common.parseDOM(container, "div", attrs={"class": "post"})

            header = common.parseDOM(posts, "h2")
            content = common.parseDOM(posts, 'div', attrs={"class": "content"})


            links = common.parseDOM(header, "a", ret="href")
            titles = common.parseDOM(header, "a")
            images = common.parseDOM(content, "img", ret="src")

            for i, title in enumerate(titles):
                items += 1

                cat = common.parseDOM(posts[i], "div", attrs={'class': 'cat'})
                genres = common.parseDOM(cat, 'a', attrs={'rel': 'category tag'})

                infos = common.parseDOM(content[i], "p")
                desc = infos[3]

                for j, info in enumerate(infos):
                    if 'strong' in info:
                        desc = common.stripTags(info)
                        genre = ', '.join(genres)

                link = links[i]
                image = images[i]

                uri = sys.argv[0] + '?mode=show&url=%s' % link
                item = xbmcgui.ListItem(title, thumbnailImage=image)
                item.setInfo(type='Video', infoLabels={'title': title, 'genre': genre, 'plot': self.unescape(desc)})

                self.favorites.addContextMenuItem(item, {'title': title.encode('utf-8'), 'url': link, 'image': image, 'playable': False, 'action': 'add', 'plugin': self.id})

                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status%s" % response["status"])

        if not items < 8:
            uri = sys.argv[0] + '?mode=%s&url=%s&page=%s' % ("category", url, str(int(page) + 1))
            item = xbmcgui.ListItem(self.language(9001), thumbnailImage=self.inext)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def getFilmInfo(self, url):
        print "*** getFilmInfo rot URL %s" % url

        response = common.fetchPage({"link": url})
        entry = common.parseDOM(response["content"], 'div', attrs={'class': 'entry'})

        flash_player = common.parseDOM(entry, "object")
        image = common.parseDOM(entry, 'img', attrs={'class': 'm_pic'}, ret='src')[0]

        uhash = common.parseDOM(flash_player, "param", attrs={"name": "flashvars"}, ret="pl")[0].split('&')[0]
        uhash = uhash.replace('"', '')

        # 1) get encoded URL from playlist/file HASH
        uppod_url = uppod.decodeSourceURL(uhash)

        # 2) get source HASH from encoded URL => getDecodedHashFromSourceURL(url, referer)
        uppod_hash = uppod.getDecodedHashFromSourceURL(uppod_url, 'http://serialu.net/media/stil-nov/uppod.swf')

        # http://serialu.net/una1.php?s=I.Hear.Your.Voice&md5=5de21a077941aaafd46e803be2a0de89&rand=0.16188193298876286

        # 3) get playlist/file from encoded HASH
        json_playlist = json.loads(uppod.decode(uppod_hash).encode('latin1').decode('utf-8'))
        playlist = json_playlist['playlist']

        if 'playlist' in playlist[0]:
            print "*** This is a playlist with several seasons"

            for season in playlist:
                episods = season['playlist']

                for episode in episods:
                    title = episode['comment']
                    uri = sys.argv[0] + '?mode=play&url=%s' % uppod.decode(episode['file'])
                    info = {'title': title, 'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0}

                    item = xbmcgui.ListItem(title, thumbnailImage=image)
                    item.setInfo(type='Video', infoLabels=info)
                    item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
        else:
            print "*** This is a playlist with one season"

            for episode in playlist:
                title = episode['comment']
                uri = sys.argv[0] + '?mode=play&url=%s' % uppod.decode(episode['file'])
                info = {'title': title, 'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0}

                item = xbmcgui.ListItem(title, thumbnailImage=image)
                item.setInfo(type='Video', infoLabels=info)
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        xbmc.executebuiltin('Container.SetViewMode(51)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def listGenres(self, url):
        print "list genres"
        #response = common.fetchPage({"link": url})
        response = self.get(url)

        container = common.parseDOM(response, "div", attrs={"class": "main-container"})
        genres = common.parseDOM(container, "div", attrs={"class": "h-menu2"})

        titles = common.parseDOM(genres, "a")[1:]
        links = common.parseDOM(genres, "a", ret="href")[1:]

        print links

        for i, title in enumerate(titles):
            uri = sys.argv[0] + '?mode=category&url=%s' % links[i]
            item = xbmcgui.ListItem(title, thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmcplugin.endOfDirectory(self.handle, True)

    def playItem(self, url):
        print "*** play url %s" % url
        item = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(self.handle, True, item)

    def get(self, url):
        cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)

        request = urllib2.Request(url)
        request.add_header('Host', 'serialu.net')
        request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.0 Safari/537.13 SUSE/24.0.1290.0')

        response = opener.open(request)
        return response.read()

    def show_favorites(self):
        self.favorites.list()
        xbmcplugin.endOfDirectory(self.handle, True)

    def search(self):
        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        kbd.setHeading(self.language(2000))
        kbd.doModal()
        keyword = ''

        if kbd.isConfirmed():
            if self.addon.getSetting('translit') == 'true':
                keyword = translit.rus(kbd.getText())
            else:
                keyword = kbd.getText()

            serach_url = "%s?s=%s" % (self.url, urllib.quote(keyword))
            self.getCategoryItems(serach_url, 1)
        else:
            self.menu()

    def showErrorMessage(self, msg):
        print msg
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("ERROR", msg, str(10 * 1000)))

    def unescape(self, string):
        return HTMLParser.HTMLParser().unescape(string) #.decode('cp1251')

    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')

plugin = SerialuNet()
plugin.main()
