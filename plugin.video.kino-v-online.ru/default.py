#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.7
# -*- coding: utf-8 -*-

import os, urllib, urllib2, sys, json #, socket, cookielib, errno
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import XbmcHelpers
common = XbmcHelpers

import Translit as translit
translit = translit.Translit(encoding='cp1251')

# FIXME: Find a better way for module import
sys.path.append(os.path.join(os.path.dirname(__file__), "../plugin.video.unified.search"))
from unified_search import UnifiedSearch


class Plugin():
    def __init__(self):
        self.id = 'plugin.video.kino-v-online.ru'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])

        self.url = 'http://kino-v-online.tv'

    def main(self):
        params = common.getParameters(sys.argv[2])
        mode = url = category = None

        mode = params['mode'] if params.has_key('mode') else None
        url = urllib.unquote_plus(params['url']) if params.has_key('url') else None
        page = params['page'] if params.has_key('page') else 1

        keyword = params['keyword'] if 'keyword' in params else None
        unified = params['unified'] if 'unified' in params else None

        if mode == 'play':
            self.playItem(url)
        if mode == 'show':
            self.show(url)
        if mode == 'category':
            self.getCategoryItems(url, page)
        if mode == 'genres':
            self.listGenres()
        if mode == 'search':
            self.search(keyword, unified)
        elif mode == None:
            self.menu()


    def menu(self):
        print "Main menu"

        uri = sys.argv[0] + '?mode=%s&url=%s'%("search", "http://kino-v-online.tv")
        item = xbmcgui.ListItem("[COLOR=FF00FF00][%s][/COLOR]"%self.language(2000), thumbnailImage = self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s'%("genres", "http://kino-v-online.tv")
        item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]"%self.language(1004), thumbnailImage = self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s'%("category", "http://kino-v-online.tv/serial-online")
        item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]"%self.language(1001), thumbnailImage = self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s'%("category", "http://kino-v-online.tv/tv-online")
        item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]"%self.language(1002), thumbnailImage = self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s'%("category", "http://kino-v-online.tv/multfilm-online")
        item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]"%self.language(1003), thumbnailImage = self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.getCategoryItems("http://kino-v-online.tv/novinki-online", "1")


    def listGenres(self):
        response = common.fetchPage({"link": self.url})

        if response["status"] == 200:
            latestnews = common.parseDOM(response["content"], "ul", attrs = { "class":"latestnews" })

            links = common.parseDOM(latestnews, "a", ret="href")[:-18]
            titles = common.parseDOM(latestnews, "a")[:-18]

            for i, title in enumerate(titles):
                uri = sys.argv[0] + '?mode=%s&url=%s'%("category", links[i])
                item = xbmcgui.ListItem(self.encode(title), thumbnailImage = self.icon)
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status%s"%response["status"])

        xbmcplugin.endOfDirectory(self.handle, True)


    def getCategoryItems(self, url, page):
        print "*** Get category items %s"%url

        page_url = "%s/page/%s/"%(url, str(int(page)))
        response = common.fetchPage({"link": page_url})
        counter = 0

        if response["status"] == 200:
            content = common.parseDOM(response["content"], "div", attrs = { "id":"dle-content" })
            contentheading = common.parseDOM(content, "td", attrs = { "class":"contentheading" })
            contentpaneopen = common.parseDOM(content, "table", attrs = { "class":"contentpaneopen" })

            titles = common.parseDOM(contentheading, "a")
            links = common.parseDOM(contentheading, "a", ret="href")
            images = common.parseDOM(contentpaneopen, "img", ret="src")
            descs = common.parseDOM(contentpaneopen, "div", attrs = { "class":"descript" })


            films = common.parseDOM(contentpaneopen, "div", attrs = { "class":"full_film" })

            for i, title in enumerate(titles):
              counter += 1

              infos = common.parseDOM(films[i], "div", attrs = { "class":"descr" })
              year = infos[0] # year
              genre = common.stripTags(self.encode(infos[1])) # genre

              title = self.encode(title).replace(self.language(5002).encode('utf-8'), '') + ' (%s)'%year
              desc = common.stripTags(self.encode(descs[i]))

              uri = sys.argv[0] + '?mode=%s&url=%s'%("show", links[i])
              item = xbmcgui.ListItem(title, thumbnailImage = images[i])
              item.setInfo( type='Video', infoLabels={"title": title, "genre": genre, "plot" : desc})
              xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status%s"%response["status"])

        if not counter < 10:
            # Next page item
            uri = sys.argv[0] + '?mode=%s&url=%s&page=%s'%("category", url, str(int(page)+1))
            item = xbmcgui.ListItem("Next page >>", thumbnailImage = self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)


    def show(self, url):
        print "*** Get movie item %s"%url
        response = common.fetchPage({"link": url})

        if response["status"] == 200:
            content = common.parseDOM(response["content"], "div", attrs = { "id":"dle-content" })
            contentheading = common.parseDOM(content, "td", attrs = { "class":"contentheading" })
            film = common.parseDOM(content, "img", attrs = { "class":"top" })

            title = self.encode(common.parseDOM(contentheading, "h1")[0])
            image = common.parseDOM(content, "img", attrs = { "class":"top" }, ret="src")[0]
            desc = common.stripTags(self.encode(common.parseDOM(film, "div", attrs = { "class":"descript" })[0]))
            player = common.parseDOM(response["content"], "object")

            movie = common.parseDOM(player, "param", attrs = { "name":"flashvars" }, ret="file")
            playlist = common.parseDOM(player, "param", attrs = { "name":"flashvars" }, ret="pl")

            if playlist:
                print "*** This is a season"
                # TODO: get Season list
                # then list episods
                self.listEpisods(playlist[0], image, desc)
            else:
                uri = sys.argv[0] + '?mode=%s&url=%s'%("play", movie[0])
                item = xbmcgui.ListItem(title, thumbnailImage = image)
                item.setInfo( type='Video', infoLabels={"title": title, "plot" : desc})
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status%s"%response["status"])

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    # TODO: list seasons and episods
    def listEpisods(self, playlist, image, desc):
        playlist = eval(playlist[:-1])['playlist']

        for item in playlist:
            title = "%s %s"%(item['comment'], self.language(5001).encode('utf-8'))

            uri = sys.argv[0] + '?mode=%s&url=%s'%("play", item['file'])
            item = xbmcgui.ListItem(title, thumbnailImage = image)
            item.setInfo( type='Video', infoLabels={"title": title, "plot" : desc})
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(self.handle, uri, item, False)


    def getVideoURL(self, url):
        request = urllib2.Request(url)
        request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        request.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3')
        request.add_header('Accept-Encoding', 'gzip,deflate,sdch')
        request.add_header('Accept-Language', 'de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4')
        request.add_header('Connection', 'keep-alive')
        request.add_header('Host', 'kino-v-online.tv')
        request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.0 Safari/537.13 SUSE/24.0.1290.0')

        response = urllib2.urlopen(request)
        return response.geturl()

    def playItem(self, url):
        print "*** protected URL %s"%url
        url = self.getVideoURL(url)
        print "*** video URL %s"%url

        item = xbmcgui.ListItem(path = url)
        xbmcplugin.setResolvedUrl(self.handle, True, item)

    def getUserInput(self):
        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        kbd.setHeading(self.language(2000))
        kbd.doModal()
        keyword = None

        if kbd.isConfirmed():
            if self.addon.getSetting('translit') == 'true':
                keyword = translit.rus(kbd.getText())
            else:
                keyword = kbd.getText()
        return keyword

    def search(self, keyword, unified):
        keyword = translit.rus(keyword) if unified else self.getUserInput()
        unified_search_results = []

        if keyword:
            url = 'http://kino-v-online.tv/index.php?do=search'

            values = {
                "do": "search",
                "full_search":	"0",
                "result_from": "1",
                "result_num": "22",
                "search_start": "a",
                "story": keyword,
                "subaction": "search"
            }

            data = urllib.urlencode(values)
            req = urllib2.Request(url, data)

            response = urllib2.urlopen(req)
            html = response.read()
            content = common.parseDOM(html, "div", attrs={"id": "dle-content"})

            if response.geturl() == url:
                links = common.parseDOM(content, "a", ret="href")
                titles = common.parseDOM(content, "b")
            else:
                links = [response.geturl().replace(self.url, '')]
                titles = common.parseDOM(content, "h1")

            images = common.parseDOM(content, "img", attrs={"class": "top"}, ret="src")

            if unified:
                for i, title in enumerate(titles):
                    if images:
                        unified_search_results.append({'title': self.encode(title), 'url':  self.url + '/' + links[i], 'image': images[i], 'plugin': self.id})
                    else:
                        unified_search_results.append({'title': self.encode(title), 'url': self.url + '/' + links[i], 'image': '', 'plugin': self.id})

                UnifiedSearch().collect(unified_search_results)

            else:
                if links:
                    for i, link in enumerate(links):
                        if not link == "#":
                            if images: 
                                uri = sys.argv[0] + '?mode=%s&url=%s'%("show", self.url + '/' + link)
                                item = xbmcgui.ListItem(self.encode(titles[i]), thumbnailImage = images[i])
                                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
                            else:
                                uri = sys.argv[0] + '?mode=%s&url=%s'%("show", self.url + '/' + link)
                                item = xbmcgui.ListItem(self.encode(titles[i]), thumbnailImage = self.icon)
                                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
                else:
                    item = xbmcgui.ListItem(self.language(2001), thumbnailImage = self.icon)
                    xbmcplugin.addDirectoryItem(self.handle, "", item, False)

        else:
            self.menu()

        xbmc.executebuiltin('Container.SetViewMode(50)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def showErrorMessage(self, msg):
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)"%("ERROR",msg, str(10*1000)))

    def strip(self, string):
        return string.replace("\xee\xed\xeb\xe0\xe9\xed", "")

    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')


class HeadRequest(urllib2.Request):
    def get_method(self):
        return 'HEAD'

def getheadersonly(url, redirections=True):
    opener = urllib2.OpenerDirector()
    opener.add_handler(urllib2.HTTPHandler())
    opener.add_handler(urllib2.HTTPDefaultErrorHandler())
    if redirections:
        # HTTPErrorProcessor makes HTTPRedirectHandler work
        opener.add_handler(urllib2.HTTPErrorProcessor())
        opener.add_handler(urllib2.HTTPRedirectHandler())
    try:
        res = opener.open(HeadRequest(url))
    except urllib2.HTTPError, res:
        pass
    res.close()

    print res.info()
    return dict(code=res.code, headers=res.info(), finalurl=res.geturl())

plugin = Plugin()
plugin.main()
