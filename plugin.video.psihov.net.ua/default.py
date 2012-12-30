#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.3
# -*- coding: utf-8 -*-

import os, urllib, urllib2, sys, socket, cookielib, errno
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import CommonFunctions
common = CommonFunctions


#from FavoritesHelpers import FavoritesHelpers
#favorites = FavoritesHelpers('plugin.video.psihov.net.ua', encoding='cp1251')

class Addon():
    def __init__(self):
        self.id = 'plugin.video.psihov.net.ua'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')

        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])
        self.url = 'http://film.psihov.net.ua'

        self.icon_search = os.path.join(self.path, 'resources/icons/search.png')
        self.icon_folder = os.path.join(self.path, 'resources/icons/folder.png')
        self.icon_next = os.path.join(self.path, 'resources/icons/next.png')


    def main(self):
        #self.sign_in()
        params = common.getParameters(sys.argv[2])
        mode = url = category = None
        mode = params['mode'] if params.has_key('mode') else None
        url = urllib.unquote_plus(params['url']) if params.has_key('url') else None
        image = params['image'] if params.has_key('image') else None
        title = params['title'] if params.has_key('title') else None

        if mode == 'play':
            self.playItem(url)
        if mode == 'search':
            self.search()
        if mode == 'alphabet':
            self.getAlphabet(url)
        if mode == 'genre':
            self.getGenres(url)
        if mode == 'season':
            self.getSeasonList(url)
        if mode == 'category':
            self.getMovieList(url)
        if mode == 'submenu':
            self.submenu(url)
        elif mode == None:
            self.menu()

    def menu(self):
        # Accept EULA if movie list is empty (move to getMovieList)
        response = common.fetchPage({"link": "http://film.psihov.net.ua/?action=setRulesRead"})

        uri = sys.argv[0] + '?mode=search'
        item = xbmcgui.ListItem('[COLOR=FF00FF00][%s][/COLOR]'%self.language(5000), iconImage = self.icon_search)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=submenu&action=films'
        item = xbmcgui.ListItem('[COLOR=FF00FFF0]%s[/COLOR]'%self.language(1000), iconImage = self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=category&url=%s'%urllib.quote_plus(self.url+'/?action=series&page=0')
        item = xbmcgui.ListItem('[COLOR=FF00FFF0]%s[/COLOR]'%self.language(1001), iconImage = self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=category&url=%s'%urllib.quote_plus('http://film.psihov.net.ua/?action=genre&genre=107&page=0')
        item = xbmcgui.ListItem('[COLOR=FF00FFF0]%s[/COLOR]'%self.language(1002), iconImage = self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.getMovieList(self.url+'/?action=news&page=0')

        xbmcplugin.endOfDirectory(self.handle, True)


    def submenu(self, action):
        url = self.url + '?action=%s'%action
        print "Submenu: %s"%url
        uri = sys.argv[0] + '?mode=alphabet&url=%s'%urllib.quote_plus('http://film.psihov.net.ua/?action=alphabet')
        item = xbmcgui.ListItem(self.language(1003), iconImage = self.icon_folder)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=genre&url=%s'%urllib.quote_plus('http://film.psihov.net.ua/?action=genre')
        item = xbmcgui.ListItem(self.language(1004), iconImage = self.icon_folder)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=category&url=%s'%urllib.quote_plus('http://film.psihov.net.ua/?action=ratingIMDB&page=0')
        item = xbmcgui.ListItem(self.language(1005), iconImage = self.icon_folder)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmcplugin.endOfDirectory(self.handle, True)


    def getMovieList(self, url):
        print "get HTML here for URL %s"%url
        response = common.fetchPage({"link": url})

        items = 0

        if response["status"] == 200:
            movies = common.parseDOM(response["content"], "div", attrs = { "class":"moviecard" })

            for i, movie in enumerate(movies):
                head = common.parseDOM(movie, "div", attrs = { "class":"mvcrhead" })
                body = common.parseDOM(movie, "div", attrs = { "class":"inf" })

                title = self.encode(common.parseDOM(head, "a")[0])
                link = urllib.quote_plus(self.url + '/' + common.parseDOM(head, "a", ret="href")[0])
                image = self.url + '/' + common.parseDOM(movie, "img", ret="src")[0]

                infos = common.parseDOM(body[0], "td")

#                print "************************************"
#                print self.encode(infos[0]) # genres
#                print infos[1]              # country
#                print infos[2]              # duration
#                print infos[3]              # quality
#                print infos[4]              # director
#                print float(infos[5])/10    # IMDB

                description = self.encode(infos[-1])
                
                try:
                    imdb = float(infos[5])/10
                    genre = 'IMDB:' + str(imdb) + ' ' + self.language(1010).encode('utf-8') + self.encode(infos[0])
                    
                    labels = {
                      'title' : title,
                      'genre' : genre,
                      'plot' : description,
                      'rating' : imdb
                    }
                except ValueError, e:
                    genre = self.language(1010).encode('utf-8') + self.encode(infos[0])

                    labels = {
                      'title' : title,
                      'genre' : genre,
                      'plot' : description
                    }

                files = common.parseDOM(body, "a", ret="href")

                if len(files) > 2:
                    print "*** Assume this is a season"

                    items = items + 1

                    uri = sys.argv[0] + '?mode=season&url=%s'%link
                    item = xbmcgui.ListItem(title, iconImage = image)

                    item.setInfo(type='Video', infoLabels= labels)
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

                else:
                    print "*** Assuming this is a movie"
                    link = urllib.quote_plus(self.url + '/' + files[0])

                    items = items + 1

                    uri = sys.argv[0] + '?mode=play&url=%s'%link
                    item = xbmcgui.ListItem(title, iconImage = image)

                    item.setInfo(type='Video', infoLabels= labels)
                    item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, False)


        else:
            self.showErrorMessage("menu(): bad response status%s"%response["status"])

        if not items < 9:
          print "show next page"
          self.nextPage(url)
        else:
          print items

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)


    def getSeasonList(self, url):
        print "*** get seasons"
        response = common.fetchPage({"link": url})

        if response["status"] == 200:
            movies = common.parseDOM(response["content"], "div", attrs = { "class":"moviecard" })
            head = common.parseDOM(movies, "div", attrs = { "class":"mvcrhead" })
            body = common.parseDOM(movies, "div", attrs = { "class":"inf" })

            table = common.parseDOM(body[1], "table")
            rows = common.parseDOM(table, "tr")

            image = self.url + '/' + common.parseDOM(movies, "img", ret="src")[0]

            for i, row in enumerate(rows):
                link = common.parseDOM(row, "a", ret="href")

                if link:
                    url = urllib.quote_plus(self.url + '/' + link[0])
                    title = self.encode(common.parseDOM(row, "a")[0])

                    uri = sys.argv[0] + '?mode=play&url=%s'%url
                    item = xbmcgui.ListItem(title, iconImage = image)

                    info = {"Title": title, "overlay": xbmcgui.ICON_OVERLAY_WATCHED, "playCount": 0}
                    item.setInfo( type='Video', infoLabels=info)
                    item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
                else:
                    continue
        else:
            self.showErrorMessage("menu(): bad response status%s"%response["status"])

        xbmc.executebuiltin('Container.SetViewMode(51)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def getGenres(self, url):
        print "*** get genres"
        print url
        response = common.fetchPage({"link": url})

        if response["status"] == 200:
            genres = common.parseDOM(response["content"], "table", attrs = {"width":"100%"})
            titles = common.parseDOM(genres[2], "a")
            links = common.parseDOM(genres[2], "a", ret="href")

            for i, link in enumerate(links):

                url = urllib.quote_plus(self.url + '/' + link + '&page=0')
                title = self.encode(titles[i])

                uri = sys.argv[0] + '?mode=category&url=%s'%url
                item = xbmcgui.ListItem(title, iconImage = self.icon_folder)
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
        else:
            self.showErrorMessage("menu(): bad response status%s"%response["status"])

        xbmcplugin.endOfDirectory(self.handle, True)


    def getAlphabet(self, url):
        print "*** getAlphabet"
        print url
        response = common.fetchPage({"link": url})

        if response["status"] == 200:
            genres = common.parseDOM(response["content"], "div", attrs = {"align":"center"})
            titles = common.parseDOM(genres[1], "a")
            links = common.parseDOM(genres[1], "a", ret="href")

            for i in range(10,len(links)):
                if(titles[i]):
                  url = urllib.quote_plus(self.url + '/' + links[i] +'&page=0')
                  title = self.encode(titles[i])

                  uri = sys.argv[0] + '?mode=category&url=%s'%url
                  item = xbmcgui.ListItem(title, iconImage = self.icon_folder)
                  xbmcplugin.addDirectoryItem(self.handle, uri, item, True)


            for i in range(0,10):
                if(titles[i]):
                  url = urllib.quote_plus(self.url + '/' + links[i]+'&page=0')
                  title = self.encode(titles[i])

                  uri = sys.argv[0] + '?mode=category&url=%s'%url
                  item = xbmcgui.ListItem(title, iconImage = self.icon_folder)
                  xbmcplugin.addDirectoryItem(self.handle, uri, item, True)


#            for i, link in enumerate(links):
#                if(titles[i]):
#                  url = urllib.quote_plus(self.url + '/' + link)
#                  title = self.encode(titles[i])

#                  uri = sys.argv[0] + '?mode=category&url=%s'%url
#                  item = xbmcgui.ListItem(title, iconImage = self.icon_folder)
#                  xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("menu(): bad response status%s"%response["status"])

        xbmcplugin.endOfDirectory(self.handle, True)


    def nextPage(self, url):
        # FIXME: do not display "Next page" if page == max page in pagination
        # or if items number less than 10
        print url

        page = url.split('=')[-1]
        if url.find('page') == -1:
            print "Not found"
        else:
            print "Found"
            uri = sys.argv[0] + '?mode=category&url=%s'%urllib.quote_plus(url+'&page=%s'%str(int(page)+1))
            item = xbmcgui.ListItem('[Next page]', iconImage = self.icon_next)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)



    def search(self):
        import Translit as translit
        translit = translit.Translit(encoding='cp1251')

        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        kbd.setHeading(self.language(5000))
        kbd.doModal()
        keyword=''

        if kbd.isConfirmed():
          keyword = kbd.getText()

          if self.addon.getSetting('translit') == 'true':
            print "*** Translit enabled keyword: %s"%keyword
            keyword = translit.rus(kbd.getText())
            print "*** Transliteration: %s"%keyword.decode('cp1251').encode('utf-8')


        url = "http://film.psihov.net.ua/?action=search&searchstring=%s&name=on&originalname=on&page=0"%keyword
        self.getMovieList(url)



    def listFavorites(self):
      favorites.listItems(playable=False)
      xbmcplugin.endOfDirectory(self.handle, True)


    def playItem(self, url):
        print "*** play url %s"%url
        item = xbmcgui.ListItem(path = url)
        xbmcplugin.setResolvedUrl(self.handle, True, item)


    def showErrorMessage(self, msg):
        print msg
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)"%("ERROR",msg, str(10*1000)))


    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')

addon = Addon()
addon.main()
