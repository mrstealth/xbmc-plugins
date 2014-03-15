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
        self.id = 'plugin.video.musicboxtv.ru'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.fanart = self.addon.getAddonInfo('fanart')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])
        self.url = 'http://musicboxtv.ru'

    def main(self):
        params = common.getParameters(sys.argv[2])
        mode = url = page = None

        mode = params['mode'] if 'mode' in params else None
        url = urllib.unquote_plus(params['url']) if 'url' in params else None
        stream = params['stream'] if 'stream' in params else None

        if mode == 'play':
            self.play(stream)
        if mode == 'category':
            self.getCategoryItems(url)
        if mode == 'channels':
            self.channels(url, group)
        elif mode == None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=play&stream=%s' % 'humorbox.sdp'
        item = xbmcgui.ListItem('Jumor TV', iconImage=self.icon, thumbnailImage='http://musicboxtv.ru/var/channels/images/1387523622.png')
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        uri = sys.argv[0] + '?mode=play&stream=%s' % 'musicbox.sdp'
        item = xbmcgui.ListItem('Musicbox', iconImage=self.icon, thumbnailImage='http://musicboxtv.ru/var/channels/images/1340118314.png')
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        uri = sys.argv[0] + '?mode=play&stream=%s' % 'musicboxtv.sdp'
        item = xbmcgui.ListItem('Russian Musicbox', iconImage=self.icon, thumbnailImage='http://musicboxtv.ru/var/channels/images/1340118370.png')
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)


        xbmcplugin.endOfDirectory(self.handle, True)

    # def getCategoryItems(self, url):
    #     print "*** Get category items %s" % url

    #     response = common.fetchPage({"link": url})

    #     if response["status"] == 200:
    #         content = common.parseDOM(response["content"], "div", attrs={"id": "content"})
    #         nav = common.parseDOM(content, "nav")

    #         channels = common.parseDOM(nav, 'h2')
    #         links = common.parseDOM(nav, 'a', ret='href')
    #         images = common.parseDOM(nav, 'img', ret='src')

    #         for i, channel in enumerate(channels):
    #             url = self.url + links[i]
    #             uri = sys.argv[0] + '?mode=channel&url=%s' % url
    #             item = xbmcgui.ListItem(group, iconImage=self.icon, thumbnailImage=self.icon)
    #             xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    #     else:
    #         self.showErrorMessage("getCategoryItems(): Bad response status%s" % response["status"])


    #     # xbmc.executebuiltin('Container.SetViewMode(52)')
    #     xbmcplugin.endOfDirectory(self.handle, True)

    def getStreamURL(self, url):
        print "*** Get channels for group %d" % group

    def play(self, stream):
        url = "rtmp://musicbox.cdnvideo.ru/musicbox-live playpath=musicbox.sdp swfUrl=http://musicboxtv.ru/_front/flowplayer.rtmp-3.2.12.swf swfVfy=true live=true"

        url = "rtmp://musicbox.cdnvideo.ru/musicbox-live"
        url += " playpath=%s" % stream
        url += " swfUrl=http://musicboxtv.ru/_front/flowplayer.rtmp-3.2.12.swf"
        url += " pageURL=http://musicboxtv.ru"
        url += " swfVfy=true live=true"

        print "URL: %s" % url
        item = xbmcgui.ListItem(path = url)
        xbmcplugin.setResolvedUrl(self.handle, True, item)

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
