#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.1
# -*- coding: utf-8 -*-

import os
import urllib
import urllib2
import sys
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import re
import XbmcHelpers
common = XbmcHelpers

import Translit as translit
translit = translit.Translit(encoding='cp1251')

from youtube import YouTubeParser

class TeremokTv():
    def __init__(self):
        self.id = 'plugin.video.teremok.tv'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])
        self.url = 'http://teremok.tv/'

        self.inext = os.path.join(self.path, 'resources/icons/next.png')
        self.debug = False

    def main(self):
        mode = url = page = playlist = None
        params = common.getParameters(sys.argv[2])
        mode = params['mode'] if 'mode' in params else None
        url = urllib.unquote_plus(params['url']) if 'url' in params else None
        page = int(params['page']) if 'page' in params else 1

        vid = params['vid'] if 'vid' in params else None
        playlist = True if 'playlist' in params else False

        if mode == 'play':
            self.play(url)
        if mode == 'show':
            self.show(vid, playlist)
        if mode == 'index':
            self.index(url, page)
        if mode == 'genres':
            self.genres()
        elif mode is None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        item = xbmcgui.ListItem("[B][COLOR=FF00FF00]%s[/COLOR][/B]" % self.language(2000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("genres", self.url)
        item = xbmcgui.ListItem("[B][COLOR=FF00FFF0]%s[/COLOR][/B]" % self.language(1000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.index('http://teremok.tv/video/', 1)
        xbmcplugin.endOfDirectory(self.handle, True)


    def genres(self):
        response = common.fetchPage({"link": self.url})
        container = common.parseDOM(response["content"], "div", attrs={"class": "menu clearfix"})

        titles = common.parseDOM(container, "a")
        links = common.parseDOM(container, "a", ret="href")

        for i, title in enumerate(titles):
            uri = sys.argv[0] + '?mode=%s&url=%s&page=1' % ("index", links[i])
            item = xbmcgui.ListItem(title, thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmcplugin.endOfDirectory(self.handle, True)


    def index(self, url, page):
        page_url = "%s/page/%d/" % (url, page)
        response = common.fetchPage({"link": page_url})

        if response["status"] == 200:
            container = common.parseDOM(response["content"], "div", attrs={"id": "content"})
            videos = common.parseDOM(container, "ul", attrs={"class": "video-list bottomdescription"})

            titles = common.parseDOM(videos, "a", attrs={"class": "cover pie"}, ret="title")
            vids = common.parseDOM(videos, "a", attrs={"class": "cover pie"}, ret='data')
            images = common.parseDOM(videos, "img", ret='src')

            descriptions = common.parseDOM(videos, "div", attrs={"class": "hidden"})

            for i, title in enumerate(titles):
                if 'PL' in vids[i]:
                    uri = sys.argv[0] + '?mode=%s&playlist=True&vid=%s' % ("show", vids[i])
                else:
                    uri = sys.argv[0] + '?mode=%s&vid=%s' % ("show", vids[i])


                title = self.stripHTML(title).capitalize()
                desc = self.stripHTML(common.stripTags(descriptions[i]))

                item = xbmcgui.ListItem(title, iconImage=images[i])
                item.setInfo(type='Video', infoLabels={ 'title': title, 'genre': 'genres', 'plot': desc })
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

            if len(titles) == 40:
                uri = sys.argv[0] + '?mode=%s&url=%s&page=%s' % ("index", url, page+1)
                item = xbmcgui.ListItem(self.language(9001), iconImage=self.inext)
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status%s" % response["status"])

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)


    def show(self, vid, playlist):
        try:
            if playlist:
                print "Get playlist videos from Youtube API"
                videos = YouTubeParser().playlist_links(vid)

                if videos:
                    for title in videos.iterkeys():
                        url = urllib.quote(videos[title])
                        uri = sys.argv[0] + '?mode=%s&url=%s' % ("play", url)

                        item = xbmcgui.ListItem(title.encode('utf-8'), thumbnailImage=self.icon)
                        item.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
                else:
                    item = xbmcgui.ListItem(self.language(9002), thumbnailImage=self.icon)
                    item.setProperty('IsPlayable', 'false')
                    xbmcplugin.addDirectoryItem(self.handle, '', item, True)

            else:
                print "Get links from Youtube API"
                url = urllib.quote("http://www.youtube.com/watch?v=%s" % vid)
                uri = sys.argv[0] + '?mode=%s&url=%s' % ("play", url)

                item = xbmcgui.ListItem(self.language(9000), thumbnailImage=self.icon)
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(self.handle, uri, item, False)


        except Exception, e:
            print "Exception %s" % str(e)
            item = xbmcgui.ListItem('Exception: %s' % str(e), thumbnailImage=self.icon)
            item.setProperty('IsPlayable', 'false')
            xbmcplugin.addDirectoryItem(self.handle, '', item, True)


        xbmcplugin.endOfDirectory(self.handle, True)

    def play(self, url):
        print "*** Watch URL %s" % url
        link = YouTubeParser().playable_link(url)
        print "*** Play %s" % link
        item = xbmcgui.ListItem(path=link)
        xbmcplugin.setResolvedUrl(self.handle, True, item)

    # === Addon helpers
    def stripHTML(self, string):
        return string.replace('&#8211;', ':').replace('&#8220;', '').replace('&#8221;', '').replace('&#8230;', '...')

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

plugin = TeremokTv()
plugin.main()
