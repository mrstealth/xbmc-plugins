#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.4
# -*- coding: utf-8 -*-

import os
import urllib
import urllib2
import cookielib
import sys
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import XbmcHelpers
common = XbmcHelpers


import Translit as translit
translit = translit.Translit(encoding='cp1251')


class KaraokeBesplatno():
    def __init__(self):
        self.id = 'plugin.video.karaoke-besplatno.ru'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])
        self.url = 'http://karaoke-besplatno.ru/'

        self.inext = os.path.join(self.path, 'resources/icons/next.png')

    def main(self):
        params = common.getParameters(sys.argv[2])
        mode = params['mode'] if 'mode' in params else None
        url = urllib.unquote_plus(params['url']) if 'url' in params else None

        if mode == 'play':
            self.playItem(url)
        if mode == 'search':
            self.search()
        if mode == 'category':
            self.getCategoryItems(url)
        if mode == 'songs':
            self.getKaraokeSongs(url)  
        elif mode is None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FF00][%s][/COLOR]" % self.language(2000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.index(self.url)
        xbmcplugin.endOfDirectory(self.handle, True)


    def index(self, url):
        response = common.fetchPage({"link": url})
        if response["status"] == 200:
            content = common.parseDOM(response["content"], "td", attrs={"class": "mframe"})
            menu = common.parseDOM(content, "td", attrs={"class": "colgray"})

            links = common.parseDOM(menu, "a", ret="href")
            titles = common.parseDOM(menu, "b")

            for i, title in enumerate(titles):
                uri = sys.argv[0] + '?mode=category&url=%s' % self.url+links[i]
                item = xbmcgui.ListItem(title, iconImage=self.icon)
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)                

        else:
            self.showErrorMessage("index(): Bad response status%s" % response["status"])

        xbmc.executebuiltin('Container.SetViewMode(50)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def getCategoryItems(self, url):
        response = common.fetchPage({"link": url})
        if response["status"] == 200:
            content = common.parseDOM(response["content"], "table", attrs={"class": "catsTable"})
            cats = common.parseDOM(content, "td", attrs={"class": "catsTd"})
            links = common.parseDOM(cats, "a", ret="href")
            titles = common.parseDOM(cats, "a")

            for i, title in enumerate(titles):
                uri = sys.argv[0] + '?mode=songs&url=%s' % links[i]
                item = xbmcgui.ListItem(title, iconImage=self.icon)
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)                

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status%s" % response["status"])
        
        xbmc.executebuiltin('Container.SetViewMode(50)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def getKaraokeSongs(self, url):
        response = common.fetchPage({"link": url})
        if response["status"] == 200:
            content = common.parseDOM(response["content"], "div", attrs={"id": "allEntries"})
            etitles = common.parseDOM(content, "div", attrs={"class": "eTitle"})
            
            image = common.parseDOM(content, "img", ret="src")[0]
            links = common.parseDOM(etitles, "a", ret="href")[1:]
            titles = common.parseDOM(etitles, "a")[1:]

            for i, title in enumerate(titles):
                uri = sys.argv[0] + '?mode=play&url=%s' % links[i]
                item = xbmcgui.ListItem(title, iconImage=self.icon, thumbnailImage=image)
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(self.handle, uri, item, False)                

        else:
            self.showErrorMessage("getKaraokeSongs(): Bad response status%s" % response["status"])
        
        xbmc.executebuiltin('Container.SetViewMode(50)')
        xbmcplugin.endOfDirectory(self.handle, True)


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

    def getVideoID(self, url):
        return url.split('/')[-1].replace('?.flv', '')


    def getVideoURL(self, vid):
        url = "http://www.youtube.com/get_video_info?video_id=%s&sts=1578&el=embedded&ps=default&eurl=&hl=en_US" % vid

        try:
            cj = cookielib.MozillaCookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            urllib2.install_opener(opener)

            request = urllib2.Request(url)
            request.add_header('Host', 'www.youtube.com')
            response = urllib2.urlopen(request, None, 10)

            tmp = response.read()

            unquoted = urllib.unquote(tmp)
            params = self.getParameters(unquoted)

            url = urllib.unquote_plus(params['url'])
            sig = params['sig']

            print "*** VIDEO ID: %s" % vid
            print "*** VIDEO URL: %s" % url    
            print "*** URL %s" % params['url']
            print "*** SIGNATURE %s" % params['sig']

            return "%s&signature=%s" % (url, sig)

        except Exception, e:
            print "### EXCEPTION: %s" % e
            self.showErrorMessage("YOUTUBE: Please try again!!!")
            return ""


    def getFlashURL(self, url):
        response = common.fetchPage({"link": url})
        
        if response["status"] == 200:
            flash = common.parseDOM(response["content"], "object")
            url = flash[0].split('file=')[-1].replace('"', '').replace('>', '')

            print "*** Found flash url %s" % url

            if "youtube" in url:
                print "*** This is a youtube URL"
                vid = self.getVideoID(url)
                url = self.getVideoURL(vid)
            elif "http" not in url:
                print "This is an URL path"
                url = self.url + url

            return url

        else:
            self.showErrorMessage("getFlashURL(): Bad response status%s" % response["status"])
        
    def playItem(self, url):
        url = self.getFlashURL(url)
        item = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(self.handle, True, item)

    def search(self):
        self.showErrorMessage("Search is not implemented")
        return ""

        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        kbd.setHeading(self.language(4000))
        kbd.doModal()
        keyword = ''

        if kbd.isConfirmed():
            if self.addon.getSetting('translit') == 'true':
                keyword = translit.rus(kbd.getText())
            else:
                keyword = kbd.getText()

            print keyword.decode('cp1251').encode('utf-8')
            url = 'http://kinoprosmotr.net/index.php?do=search'

            # Advanced search: titles only
            values = {
                "do": "search",
                "full_search": 0,
                "result_from": 1,
                "result_num":  20,
                "search_start": 1,
                "story": keyword,
                "subaction": "search"
            }

            data = urllib.urlencode(values)
            request = urllib2.Request(url, data)
            response = urllib2.urlopen(request)

            containers = common.parseDOM(response.read(), "div", attrs={"class": "search_item clearfix"})
            search_item_prev = common.parseDOM(containers, "div", attrs={"class": "search_item_prev"})
            search_item_inner = common.parseDOM(containers, "div", attrs={"class": "search_item_inner"})

            descriptions = common.parseDOM(search_item_inner, "div")

            # containers = common.parseDOM(response.read(), "div", attrs={"class": "search_item clearfix"})
            header = common.parseDOM(search_item_inner, "h3")

            titles = common.parseDOM(header, "a")
            links = common.parseDOM(header, "a", ret="href")
            images = common.parseDOM(search_item_prev, "img", ret="src")

            gcont = common.parseDOM(search_item_inner, "span")
            # descs = common.parseDOM(containers, "a", attrs = { "class":"screenshot" }, ret="title")

            if titles:
                for i, title in enumerate(titles):
                    genres = self.encode(', '.join(common.parseDOM(gcont[i], "a")))
                    desc = self.encode(common.stripTags(descriptions[i]))
                    uri = sys.argv[0] + '?mode=film&url=%s' % links[i]
                    item = xbmcgui.ListItem(self.encode(title), iconImage=self.icon, thumbnailImage=images[i])
                    item.setInfo(type='Video', infoLabels={'title': self.encode(title), 'genre': genres, 'plot': desc})

                    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
            else:
                item = xbmcgui.ListItem(self.language(4001), iconImage=self.icon, thumbnailImage=self.icon)
                xbmcplugin.addDirectoryItem(self.handle, '', item, True)

        else:
            self.menu()

        xbmcplugin.endOfDirectory(self.handle, True)

    def showErrorMessage(self, msg):
        print msg
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("ERROR", msg, str(10 * 1000)))

    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')

plugin = KaraokeBesplatno()
plugin.main()
