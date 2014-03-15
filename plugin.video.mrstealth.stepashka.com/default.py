#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *  Copyright (C) 2011 MrStealth
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# */
#
# Writer (c) 2012, MrStealth
# Rev. 1.0.2

import os
import re
import sys
import json
import xppod
import urllib
import urllib2

import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import XbmcHelpers
common = XbmcHelpers

import Translit as translit
translit = translit.Translit(encoding='cp1251')


class Stepashka():
    def __init__(self):
        self.id = 'plugin.video.mrstealth.stepashka.com'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.fanart = self.addon.getAddonInfo('fanart')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])
        self.url = 'http://online.stepashka.com/'

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
            self.listGenres()
        if mode == 'movie':
            self.getMovieItem(url)
        if mode == 'category':
            self.getCategoryItems(url, page)
        elif mode is None:
            self.menu()

    def menu(self):

        # uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        # item = xbmcgui.ListItem("[COLOR=FF00FF00][%s][/COLOR]" % self.language(2000), thumbnailImage=self.icon)
        # xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("genres", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(2001), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("category", self.url+'/filmy')
        item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(2002), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("category", self.url+'/serialy')
        item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(2003), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("category", self.url+'/tv')
        item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(2004), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("category", self.url+'/filmy/dokumentalenye/')
        item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(2005), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.getCategoryItems(self.url, 1)

        xbmcplugin.endOfDirectory(self.handle, True)

    def getCategoryItems(self, url, page):
        print "*** Get category items %s" % url
        page_url = "%s/page/%s/" % (url, str(int(page)))
        response = common.fetchPage({"link": page_url})
        items = 0

        if response["status"] == 200:
            content = common.parseDOM(response["content"], "div", attrs={"id": "dle-content"})
            movies = common.parseDOM(content, "div", attrs={"class": "dpad"})
            header = common.parseDOM(movies, "h2", attrs={"class": "btl"})

            titles = common.parseDOM(header, "a")
            links = common.parseDOM(header, "a", ret="href")
            images = common.parseDOM(movies, "img", attrs={"id": "single_image"}, ret="src")

            pagenav = common.parseDOM(response["content"], "div", attrs={"class": "navigation"})

            for i, title in enumerate(titles):
                infos = common.parseDOM(movies[i], "div", attrs={"style": "display:inline;"})[0]
                desc = common.stripTags(infos.split('</b></div><br /><br />')[-1].encode('utf-8'))
                info = common.stripTags(common.parseDOM(infos, "div", attrs={"align": "right"})[0])

                items += 1
                uri = sys.argv[0] + '?mode=movie&url=%s' % links[i]
                item = xbmcgui.ListItem(title, iconImage=self.icon, thumbnailImage=images[i])
                info = {
                    'title': title,
                    'genre': info,
                    'plot': desc
                }

                item.setInfo(type='Video', infoLabels=info)
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status%s" % response["status"])

        if pagenav and not items < 7:
            uri = sys.argv[0] + '?mode=%s&url=%s&page=%s' % ("category", url, str(int(page) + 1))
            item = xbmcgui.ListItem(self.language(4000), iconImage=self.inext)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def getMovieItem(self, url):
        print "*** Get movie item: %s" % url
        response = common.fetchPage({"link": url})

        content = common.parseDOM(response["content"], "div", attrs={"id": "dle-content"})
        movie = common.parseDOM(content, "div", attrs={"class": "dpad"})

        flashvars = common.parseDOM(movie, "param", attrs={"name": "flashvars"}, ret="value")

        title = common.parseDOM(movie, "h1", attrs={"class": "btl"})[0]
        image = common.parseDOM(movie, "img", attrs={"id": "single_image"}, ret="src")[0]

        infos = common.parseDOM(movie, "div", attrs={"style": "display:inline;"})[0]
        desc = common.stripTags(infos.split('</b></div><br /><br />')[-1].encode('utf-8'))
        info = common.stripTags(common.parseDOM(infos, "div", attrs={"align": "right"})[0])

        if 'file' in flashvars[0].split('&')[-1]:
            print "This is a movie"
            file_hash = flashvars[0].split('&')[-1].replace('file=', '')
            url = xppod.Decode(file_hash)

            uri = sys.argv[0] + '?mode=play&url=%s' % url
            item = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image)
            info = {
                'title': title,
                'genre': info,
                'plot': desc,
                'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0
            }

            item.setInfo(type='Video', infoLabels=info)
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
            xbmc.executebuiltin('Container.SetViewMode(52)')

        elif 'pl' in flashvars[0].split('&')[-1]:
            file_hash = flashvars[0].split('&')[-1].replace('pl=', '')
            print "This is a season"

            url = xppod.Decode(file_hash)
            pattern = re.compile('[\w\d=.,+]+', re.S)
            xppod_hash = pattern.findall(self.getPlaylist(url))[0]
            jsdata = xppod.Decode(xppod_hash)

            try:
                response = json.loads(jsdata.encode('latin1').decode('utf-8'))
            except Exception, e:
                print e

            if 'playlist' in response['playlist'][0]:
                print "This is a season multiple seasons"

                seasons = response['playlist']


                for season in seasons:
                    episods = season['playlist']

                    for episode in episods:
                        try:
                            uri = sys.argv[0] + '?mode=play&url=%s' % episode['file']
                            item = xbmcgui.ListItem(episode['comment'], iconImage=image, thumbnailImage=image)
                            info = {
                                'title': title,
                                'genre': info,
                                'plot': desc,
                                'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0
                            }

                            item.setInfo(type='Video', infoLabels=info)
                            item.setProperty('IsPlayable', 'true')
                            xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
                            xbmc.executebuiltin('Container.SetViewMode(51)')

                        except KeyError:
                            tmp = episode['playlist']
                            for episode in tmp:
                                uri = sys.argv[0] + '?mode=play&url=%s' % episode['file']
                                item = xbmcgui.ListItem(episode['comment'], iconImage=image, thumbnailImage=image)
                                info = {
                                    'title': title,
                                    'genre': info,
                                    'plot': desc,
                                    'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0
                                }

                                item.setInfo(type='Video', infoLabels=info)
                                item.setProperty('IsPlayable', 'true')
                                xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
                                xbmc.executebuiltin('Container.SetViewMode(51)')


            else:
                print "This is one season"

                for episode in response['playlist']:
                    etitle = episode['comment']
                    url = episode['file']

                    uri = sys.argv[0] + '?mode=play&url=%s' % url
                    item = xbmcgui.ListItem(etitle, iconImage=image, thumbnailImage=image)
                    info = {
                        'title': title,
                        'genre': info,
                        'plot': desc,
                        'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0
                    }

                    item.setInfo(type='Video', infoLabels=info)
                    item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
                    xbmc.executebuiltin('Container.SetViewMode(51)')
        else:
            print "Wrong flash vars"

        xbmcplugin.endOfDirectory(self.handle, True)

    def getPlaylist(self, url):
        request = urllib2.Request(url, None)
        request.add_header('Referer', 'http://online.stepashka.com/player/uppod.swf')
        response = urllib2.urlopen(request)
        return response.read()

    def listGenres(self):
        response = common.fetchPage({"link": self.url})

        if response["status"] == 200:
            header = common.parseDOM(response["content"], "div", attrs={"id": "header"})
            subcat = common.parseDOM(header, "ul", attrs={"class": "subcat"})

            links = common.parseDOM(subcat, "a", ret="href")[:-6]
            titles = common.parseDOM(subcat, "a")[:-6]

            for i, title in enumerate(titles):
                if i != 25:
                    uri = sys.argv[0] + '?mode=%s&url=%s' % ("category", self.url + links[i])
                    item = xbmcgui.ListItem(self.encode(title), thumbnailImage=self.icon)
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
        else:
            self.showErrorMessage("listGenres(): Bad response status%s" % response["status"])

        xbmcplugin.endOfDirectory(self.handle, True)

    def playItem(self, url):
        print "*** play url %s" % url
        item = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(self.handle, True, item)

    # XBMC helpers
    def showErrorMessage(self, msg):
        print msg
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("ERROR", msg, str(10 * 1000)))

    # Python helpers
    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')

    def convert(s):
        try:
            return s.group(0).encode('latin1').decode('utf8')
        except:
            return s.group(0)

plugin = Stepashka()
plugin.main()
