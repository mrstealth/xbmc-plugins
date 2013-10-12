#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.2
# -*- coding: utf-8 -*-

import os
import sys
import base64
import urllib
import httplib

import xml.dom.minidom as Minidom
import xml.etree.ElementTree as ElementTree

import xbmcplugin
import xbmcgui
import xbmcaddon

# FIXME: Add more formats
IMAGE_FORMATS = ['jpg', 'jpeg', 'bmp', 'png', 'gif', 'gif', 'tiff', 'mng', 'ico', 'pcx', 'raw', 'rar', 'zip']

class YandexDiskClient(object):
    def __init__(self):
        self.id = 'plugin.image.yandex.disk'
        self.addon = xbmcaddon.Addon(self.id)

        self.username = self.addon.getSetting('username')
        self.password = self.addon.getSetting('password')

        self.token = "Basic %s" % base64.encodestring(self.username + ':' + self.password).strip()
        self.host = 'webdav.yandex.ru'

        self.connection = httplib.HTTPSConnection(self.host)

    def isFile(self, path):
        return '.' in path

    def isArchive(self, format):
        return ('zip' or 'rar') in format

    def ll(self, path):
        headers = {
            "Host": "webdav.yandex.ru",
            "Accept": "*/*",
            "Depth": 1,
            "Authorization": self.token
        }

        self.connection.set_debuglevel(1)
        self.connection.request("PROPFIND", path.replace(' ', '%20'), "", headers)
        response = self.connection.getresponse().read()

        names = ElementTree.fromstring(response).findall("./{DAV:}response/{DAV:}propstat/{DAV:}prop/{DAV:}displayname")
        hrefs = ElementTree.fromstring(response).findall("./{DAV:}response/{DAV:}href")

        directories = dict([(name.text, hrefs[i].text) for i, name in enumerate(names)])
        upath = path[1:][:-1].decode('utf-8')

        blacklist = ['._.DS_Store', '.DS_Store', 'disk', upath, path]

        for blacklist_dir in blacklist:
            if blacklist_dir in directories:
                directories.pop(blacklist_dir)


        return directories

    def pretty_print(self, xml):
        parsed = Minidom.parseString(xml)
        lines  = parsed.toprettyxml(indent=' '*4).split('\n')
        return '\n'.join([line for line in lines if line.strip()])


class YandexDisk():
    def __init__(self):
        self.id = 'plugin.image.yandex.disk'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.xpath = sys.argv[0]
        self.handle = int(sys.argv[1])
        self.params = sys.argv[2]

        self.yandex_disk = os.path.join(self.path, 'resources/media/yandex_disk.png')
        self.yandex_video = os.path.join(self.path, 'resources/media/yandex_video.png')
        self.yandex_photo = os.path.join(self.path, 'resources/media/yandex_photo.png')
        self.yandex_music = os.path.join(self.path, 'resources/media/yandex_music.png')

        self.client = YandexDiskClient()
        self.debug = True

    def main(self):
        params = YandexDiskHelper().getParameters(self.params)
        mode = params['mode'] if 'mode' in params else None
        url = urllib.unquote(params['url']) if 'url' in params else None

        keyword = params['keyword'] if 'keyword' in params else None
        unified = params['unified'] if 'unified' in params else None

        if mode == 'play':
            self.play(url)
        if mode == 'list':
            self.listDirectories(url)
        elif mode is None:
            self.menu()

    def menu(self):
        if self.client.username and self.client.password:
            self.listDirectories('/')
            xbmcplugin.endOfDirectory(self.handle, True)
        else:
            self.addon.openSettings()

    def listDirectories(self, path):
        self.log("List directories for %s" % path)

        for name, path in self.client.ll(path).iteritems():
            if self.client.isFile(path):
                format = path.split('.')[-1].lower()
                if format in IMAGE_FORMATS:
                    if self.client.isArchive(format):
                        preview_icon = self.yandex_disk
                    else:
                        size = self.addon.getSetting('previewicon_size')
                        preview_icon = "https://%s:%s@webdav.yandex.com/%s?preview&size=%s" % (self.client.username, self.client.password, path, size)

                    url = "https://%s:%s@webdav.yandex.com%s" % (self.client.username, self.client.password, path)
                    item = xbmcgui.ListItem(name, iconImage=self.yandex_photo, thumbnailImage=preview_icon)
                    xbmcplugin.addDirectoryItem(self.handle, url, item, False)

                    xbmc.executebuiltin('Container.SetViewMode(53)')
                else:
                    xbmc.executebuiltin('Container.SetViewMode(50)')
            else:
                uri = sys.argv[0] + '?mode=list&url=%s' % path
                item = xbmcgui.ListItem(name, iconImage=self.yandex_disk, thumbnailImage=self.folder_icon(name))
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

                xbmc.executebuiltin('Container.SetViewMode(50)')

        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.endOfDirectory(self.handle, True)

    def play(self, path):
        url = "https://%s:%s@webdav.yandex.com%s" % (self.client.username, self.client.password, path)

        item = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(self.handle, True, item)
        xbmcplugin.endOfDirectory(self.handle, True)

    # *** Add-on helpers
    def folder_icon(self, name):
        foto = [u'\u0424\u043e\u0442\u043e\u043a\u0430\u043c\u0435\u0440\u0430', u'\u041a\u0430\u0440\u0442\u0438\u043d\u043a\u0438', u'\u0424\u043e\u0442\u043e']
        video = [u'\u0412\u0438\u0434\u0435\u043e']
        music = [u'\u041c\u0443\u0437\u044b\u043a\u0430']

        if name in music:
            return self.yandex_music
        elif name in foto:
            return self.yandex_photo
        elif name in video:
            return self.yandex_video
        else:
            return self.yandex_disk

    def log(self, message):
        if self.debug:
            print "+++ %s: %s" % (self.id, message)


class YandexDiskHelper(object):
    def getParameters(self, parameterString):
        commands = {}
        splitCommands = parameterString[parameterString.find('?') + 1:].split('&')

        for command in splitCommands:
            if (len(command) > 0):
                splitCommand = command.split('=')
                key = splitCommand[0]
                value = splitCommand[1]
                commands[key] = value

        return commands

YandexDisk().main()
