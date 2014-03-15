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
# Rev. 1.0.0

import os, urllib, urllib2, sys, socket, cookielib, errno
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
# import json
import XbmcHelpers
common = XbmcHelpers

# import Translit as translit
# translit = translit.Translit(encoding='cp1251')


class Axenttv():
    def __init__(self):
        self.id = 'plugin.video.axenttv.ru'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.fanart = self.addon.getAddonInfo('fanart')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])
        self.url = 'http://axenttv.ru/iptv_online/russian.html'

    def main(self):
        params = common.getParameters(sys.argv[2])
        mode = url = page = None

        mode = params['mode'] if 'mode' in params else None
        url = urllib.unquote_plus(params['url']) if 'url' in params else None
        group = int(params['group']) if 'group' in params else None
        page = params['page'] if 'page' in params else 1

        if mode == 'play':
            self.playItem(url)
        if mode == 'category':
            self.getCategoryItems(url)
        if mode == 'channels':
            self.channels(url, group)
        elif mode == None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=category&url=%s' % 'http://axenttv.ru/iptv_online/russian.html'
        item = xbmcgui.ListItem('Russian', iconImage=self.icon, thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=category&url=%s' % 'http://axenttv.ru/iptv_online/ukraine.html'
        item = xbmcgui.ListItem('Ukraine', iconImage=self.icon, thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        # self.getCategoryItems(self.url, 1)
        xbmcplugin.endOfDirectory(self.handle, True)

    def getCategoryItems(self, url):
        print "*** Get category items %s" % url

        response = common.fetchPage({"link": url})

        if response["status"] == 200:
            content = common.parseDOM(response["content"], "select", attrs={"id": "ch"})
            groups = common.parseDOM(content, "optgroup", ret='label')

            for i, group in enumerate(groups):
                collection = group.split('.')
                group = "%s - %s %d" % (collection[0], collection[1][:-1].lower(), i+1)

                uri = sys.argv[0] + '?mode=channels&url=%s&group=%d' % (url, i)
                item = xbmcgui.ListItem(group, iconImage=self.icon, thumbnailImage=self.icon)
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status%s" % response["status"])


        # xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def channels(self, url, group):
        print "*** Get channels for group %d" % group

        response = common.fetchPage({"link": url})

        if response["status"] == 200:
            content = common.parseDOM(response["content"], "select", attrs={"id": "ch"})
            groups = common.parseDOM(content, "optgroup", ret='label')
            options = common.parseDOM(content, "optgroup")

            options = options[group].encode('utf-8')
            titles = common.parseDOM(options, "option")
            streams = common.parseDOM(options, "option", ret='value')

            channels = {}

            for i, title in enumerate(titles):
                channels[title] = streams[i]

            for channel in sorted(channels.iterkeys()):
                try:
                    if 'HD' in channel:
                        continue
                    else:
                        uri = sys.argv[0] + '?mode=play&url=%s' % channels[channel]
                        item = xbmcgui.ListItem(channel, iconImage=self.icon, thumbnailImage=self.icon)
                        item.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
                except IndexError:
                    print "No stream URL for %s" % channel.encode('utf-8')

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status%s" % response["status"])

        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.endOfDirectory(self.handle, True)

    def playItem(self, url):
        print "*** play url %s" % url

        try:
            self.showMessage("Play URL: %s" % url)
            item = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(self.handle, True, item)
        except Exception, e:
            self.showErrorMessage(e)

    # XBMC helpers
    def showMessage(self, msg):
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("Info", msg, str(5 * 1000)))

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

plugin = Axenttv()
plugin.main()
