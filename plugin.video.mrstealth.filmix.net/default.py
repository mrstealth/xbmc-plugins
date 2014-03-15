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
# Rev. 1.0.1

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
        self.id = 'plugin.video.mrstealth.filmix.net'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.fanart = self.addon.getAddonInfo('fanart')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])
        self.url = 'http://filmix.net'

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
        if mode == 'show':
            self.show(url)
        if mode == 'category':
            self.getCategoryItems(url, page)
        elif mode == None:
            self.menu()

    def menu(self):

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FF00][%s][/COLOR]" % self.language(2000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("genres", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(1000), thumbnailImage=self.icon)
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
            blocks = common.parseDOM(content, "div", attrs={"class": "block"})

            headers = common.parseDOM(blocks, "h2")
            bodies = common.parseDOM(blocks, "div", attrs={"class": "body"})
            posts = common.parseDOM(blocks, "div", attrs={"class": "text post"})
            infos = common.parseDOM(blocks, "div", attrs={"class": "info-box"})

            titles = common.parseDOM(headers, "a")
            links = common.parseDOM(headers, "a", ret="href")
            images = common.parseDOM(posts, "img", attrs={"style": "float:left;"}, ret="src")

            pagenav = common.parseDOM(response["content"], "div", attrs={"class": "pages"})

            for i, title in enumerate(titles):
                items += 1

                title = self.encode(title)
                desc = self.encode(posts[i].split('<br />')[1])
                genre = common.parseDOM(infos[i], "li", attrs={"class": "genre"})
                genres = self.encode(', '.join(common.parseDOM(genre, "a")))

                uri = sys.argv[0] + '?mode=show&url=%s' % links[i]
                item = xbmcgui.ListItem(title, iconImage=self.icon, thumbnailImage=self.url + images[i])
                item.setInfo(type='Video', infoLabels={'title': title, 'plot': desc, 'genre': genres})
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status%s" % response["status"])

        if pagenav and not items < 9:
            uri = sys.argv[0] + '?mode=%s&url=%s&page=%s' % ("category", url, str(int(page) + 1))
            item = xbmcgui.ListItem(self.language(9001), thumbnailImage=self.inext)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def show(self, url):
        print "*** Get film/episods %s" % url

        response = common.fetchPage({"link": url})

        if response["status"] == 200:
            content = common.parseDOM(response["content"], "div", attrs={"id": "dle-content"})

            body = common.parseDOM(content, "div", attrs={"class": "body"})
            post = common.parseDOM(content, "div", attrs={"class": "text post"})
            info = common.parseDOM(content, "div", attrs={"class": "info-box"})

            player = common.parseDOM(content, "object")

            film = common.parseDOM(player, "param", attrs={"name": "flashvars"}, ret="file")
            season = common.parseDOM(player, "param", attrs={"name": "flashvars"}, ret="pl")

            title = common.parseDOM(content, "h1")[0]
            image = common.parseDOM(post, "img", attrs={"style": "float:left;"}, ret="src")[0]

            title = self.encode(title)
            image = image if 'http' in image else self.url + image

            desc = self.encode(post[0].split('<br />')[1])
            genre = common.parseDOM(info, "li", attrs={"class": "genre"})
            genres = self.encode(', '.join(common.parseDOM(genre, "a")))

            if film:
                uppod_url = film[0].split('&amp;')[0]
                url = xppod.Decode(uppod_url.replace('"', ''))

                uri = sys.argv[0] + '?mode=play&url=%s' % url
                item = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image)
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
                print "This is a season"

                uppod_url = season[0].split('&amp;')[0]
                url = xppod.Decode(uppod_url.replace('"', ''))
                uhash = self.getPlaylist(url)

                try:
                    playlist = xppod.Decode(uhash)

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
            self.showErrorMessage("show(): Bad response status%s" % response["status"])

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
            sidebar = common.parseDOM(response["content"], "div", attrs={"class": "block categories"})
            subcat = common.parseDOM(sidebar, "ul", attrs={"class": "categories"})
            print sidebar

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
            url = 'http://filmix.net/index.php?do=search'

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
                    header  = common.parseDOM(block, "h2")
                    img_cotainer = common.parseDOM(block, "div", attrs={"class": "image"})

                    title = self.encode(common.stripTags(common.parseDOM(header, "a")[0]))
                    link = common.parseDOM(header, "a", ret="href")[0]
                    image = common.parseDOM(block, "img", ret="src")[0]

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
