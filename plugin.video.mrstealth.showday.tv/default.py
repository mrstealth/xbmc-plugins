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
# Rev. 1.0.3

import os, urllib, urllib2, sys, socket, cookielib, errno
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import json
import xppod
import XbmcHelpers
common = XbmcHelpers

import Translit as translit
translit = translit.Translit(encoding='cp1251')


class Showday():
    def __init__(self):
        self.id = 'plugin.video.mrstealth.showday.tv'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.fanart = self.addon.getAddonInfo('fanart')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])
        self.url = 'http://showday.tv'

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
        if mode == 'episode':
            self.getSeasonEpisods(url)
        if mode == 'category':
            self.getSeasons(url, page)
        elif mode == None:
            self.menu()

    def menu(self):

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FF00][%s][/COLOR]" % self.language(2000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("genres", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(1000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.getSeasons(self.url, 1)

        xbmcplugin.endOfDirectory(self.handle, True)

    def getSeasons(self, url, page):
        print "*** Get category items %s" % url
        page_url = "%s/page/%s/" % (url, str(int(page)))
        response = common.fetchPage({"link": page_url})
        items = 0

        if response["status"] == 200:
            content = common.parseDOM(response["content"], "div", attrs={"id": "dle-content"})
            blocks = common.parseDOM(content, "div", attrs={"class": "block"})

            header = common.parseDOM(blocks, "h4")
            image_container = common.parseDOM(blocks, "div", attrs={"class": "image"})

            titles = common.parseDOM(header, "a")
            links = common.parseDOM(header, "a", ret="href")
            images = common.parseDOM(image_container, "img", ret="src")

            news = common.parseDOM(content, "p", attrs={"class": "new"})

            pagenav = common.parseDOM(response["content"], "div", attrs={"class": "pages"})

            for i, title in enumerate(titles):
                items += 1
                uri = sys.argv[0] + '?mode=episode&url=%s' % links[i]

                try:
                    item = xbmcgui.ListItem(self.encode(common.stripTags(title + ' (' + news[i] + ')')), iconImage=self.icon, thumbnailImage=self.url + images[i])
                except IndexError:
                    item = xbmcgui.ListItem(self.encode(title), iconImage=self.icon, thumbnailImage=self.url + images[i])
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status%s" % response["status"])

        if pagenav and not items < 16:
            uri = sys.argv[0] + '?mode=%s&url=%s&page=%s' % ("category", url, str(int(page) + 1))
            item = xbmcgui.ListItem(self.language(9001), thumbnailImage=self.inext)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def getSeasonEpisods(self, url):
        print "*** Get episods %s" % url
        response = common.fetchPage({"link": url})

        if response["status"] == 200:
            content = response["content"]
            player = common.parseDOM(content, "object", attrs={"id": "showday"})
            pl = common.parseDOM(player, "param", attrs={"name": "flashvars"}, ret="pl")
            url = xppod.Decode(pl[0].replace('"', ''))

            uhash = self.getPlaylist(url)
            playlist = xppod.Decode(uhash)

            image_container = common.parseDOM(content, "div", attrs={"class": "image"})
            image = self.url + common.parseDOM(image_container, "img", ret="src")[0]

            text = common.parseDOM(content, "div", attrs={"class": "text"})
            infos = common.parseDOM(text, "p")

            title = self.encode(common.parseDOM(text, "h4")[0])
            desc = common.stripTags(self.encode(infos[0]))
            genres = self.encode(', '.join(common.parseDOM(infos[1], "a")))

            try:
                response = eval(playlist.replace('\t', '').replace('\r\n', '').encode('latin1').decode('utf-8'))

                if 'playlist' in response['playlist'][0]:
                    print "This is a season multiple seasons"

                    seasons = response['playlist']

                    for season in seasons:
                        episods = season['playlist']

                        for episode in episods:
                            uri = sys.argv[0] + '?mode=play&url=%s' % episode['file']
                            item = xbmcgui.ListItem(episode['comment'], iconImage=image, thumbnailImage=image)
                            info = {
                                'title': title,
                                'genre': genres,
                                'plot': desc,
                                'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0
                            }

                            item.setInfo(type='Video', infoLabels=info)
                            item.setProperty('IsPlayable', 'true')
                            xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

                else:
                    print "This is one season"

                    for episode in response['playlist']:
                        etitle = episode['comment']
                        url = episode['file']

                        uri = sys.argv[0] + '?mode=play&url=%s' % url
                        item = xbmcgui.ListItem(etitle, iconImage=image, thumbnailImage=image)
                        info = {
                            'title': title,
                            'genre': genres,
                            'plot': desc,
                            'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0
                        }

                        item.setInfo(type='Video', infoLabels=info)
                        item.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
            except Exception, e:
                print e

        else:
            self.showErrorMessage("getMovie(): Bad response status%s" % response["status"])

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def getPlaylist(self, url):
        request = urllib2.Request(url, None)
        request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:18.0) Gecko/20100101 Firefox/18.0')
        request.add_header('Accept', '*')
        request.add_header('Accept-Encoding', 'gzip, deflate')
        request.add_header('Accept-Language', 'de-de,de;q=0.8,en-us;q=0.5,en;q=0.3')
        request.add_header('Referer', 'http://showday.tv/uppod.swf')

        response = urllib2.urlopen(request)
        return response.read()

    def listGenres(self):
        response = common.fetchPage({"link": self.url})

        if response["status"] == 200:
            header = common.parseDOM(response["content"], "div", attrs={"id": "header"})
            subcat = common.parseDOM(header, "ul", attrs={"class": "subcat"})

            links = common.parseDOM(subcat, "a", ret="href")
            titles = common.parseDOM(subcat, "a")

            for i, title in enumerate(titles):
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

            print keyword.decode('cp1251').encode('utf-8')
            url = 'http://showday.tv/index.php?do=search'

            # Advanced search: titles only
            values = {
                "beforeafter": "after",
                "catlist[]": "0",
                "do": "search",
                "full_search": "1",
                "replyless": "0",
                "replylimit": "0",
                "resorder": "desc",
                "result_from":  "1",
                "search_start": "1",
                "searchdate": "0",
                "searchuser": "",
                "showposts": "0",
                "sortby": "date",
                "story": keyword,
                "subaction": "search",
                "titleonly": "3"
            }

            data = urllib.urlencode(values)
            request = urllib2.Request(url, data)
            response = urllib2.urlopen(request).read()

            container = common.parseDOM(response, "div", attrs={"id": "dle-content"})
            blocks = common.parseDOM(container, "div", attrs={"class": "block"})[1:]

            if blocks:
                for i, block in enumerate(blocks):
                    text_container  = common.parseDOM(block, "div", attrs={"class": "text"})
                    img_cotainer = common.parseDOM(block, "div", attrs={"class": "image"})

                    title = self.encode(common.stripTags(common.parseDOM(text_container, "a")[0]))
                    link = common.parseDOM(text_container, "a", ret="href")[0]
                    image = common.parseDOM(img_cotainer, "img", ret="src")[0]

                    uri = sys.argv[0] + '?mode=episode&url=%s' % link
                    item = xbmcgui.ListItem(title, thumbnailImage=self.url + image)
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
            else:
                item = xbmcgui.ListItem(self.language(2001), iconImage=self.icon, thumbnailImage=self.icon)
                xbmcplugin.addDirectoryItem(self.handle, '', item, True)
        else:
            self.menu()

        xbmc.executebuiltin('Container.SetViewMode(50)')
        xbmcplugin.endOfDirectory(self.handle, True)

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

plugin = Showday()
plugin.main()
