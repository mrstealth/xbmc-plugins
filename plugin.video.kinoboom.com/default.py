#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.3
# -*- coding: utf-8 -*-

import urllib, urllib2, socket
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import XbmcHelpers
common = XbmcHelpers

class Kinoboom():
    def __init__(self):
        self.id = 'plugin.video.kinoboom.com'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])
        self.url = 'http://kinoboom.com/'

    def main(self):
        params = common.getParameters(sys.argv[2])
        mode = url = category = None

        mode = params['mode'] if params.has_key('mode') else None
        url = urllib.unquote_plus(params['url']) if params.has_key('url') else None
        category = params['category'] if params.has_key('category') else None

        if mode == 'play':
            self.playItem(url)
        if mode == 'items':
            self.getItems(url,category)
        if mode == 'seasons':
            self.getSeasonsCatalog(url)
        if mode == 'season':
            self.getSeasonItems(url)
        if mode == 'episodes':
            self.getNewEpisods(self.url)
        if mode == 'categories':
            self.getCategories(self.url)
        elif mode == None:
            self.menu()

    def menu(self):
      uri = sys.argv[0] + '?mode=categories&url=%s'%self.url
      item = xbmcgui.ListItem('[COLOR=FF00FFF0]'+self.language(2001)+'[/COLOR]', iconImage = self.icon, thumbnailImage = self.icon)
      xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

      uri = sys.argv[0] + '?mode=seasons&url=http://kinoboom.com/razdel/serialy'
      item = xbmcgui.ListItem('[COLOR=FF00FFF0]'+self.language(2002)+'[/COLOR]', iconImage = self.icon, thumbnailImage = self.icon)
      xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

      self.getItems( self.url, self.language(2000))

      xbmcplugin.endOfDirectory(self.handle, True)

    def getCategories(self, url):
        response = common.fetchPage({"link": url})

        if response["status"] == 200:
            menu = common.parseDOM(response["content"], "div", attrs = { "class":"s-block menu" })[0]
            categories = common.parseDOM(menu, "a")

            titles = common.parseDOM(menu, "a")[1:]
            categories = common.parseDOM(menu, "a", ret="title")[1:]
            links = common.parseDOM(menu, "a", ret="href")[1:]

            for i,title in enumerate(titles):
                uri = sys.argv[0] + '?mode=items&url=%s'%links[i] + '&category=%s'%categories[i]
                item = xbmcgui.ListItem(title, iconImage = self.icon, thumbnailImage = self.icon)
                item.setInfo( type="Video", infoLabels={ "Title": title } )
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
        else:
            showErrorMessage("*** ERROR in index(), bad response status%s"%response["status"])

        xbmcplugin.endOfDirectory(self.handle, True)

    def getItems(self, url, category):
        response = common.fetchPage({"link": url})

        if response["status"] == 200:
            itemslist = common.parseDOM(response["content"], "div", attrs = { "class":"items-list" })[0]

            images = common.parseDOM(itemslist, "div", attrs = { "class":"image" })
            buttons = common.parseDOM(itemslist, "div", attrs = {"class":"buttons"})

            titles = common.parseDOM(images, "a", ret="title")
            images = common.parseDOM(images, "img", ret="src")
            infos = common.parseDOM(buttons, "a", attrs = {"class":"info"}, ret="href")


            for i, title in enumerate(titles):
                item = xbmcgui.ListItem(title, iconImage = self.icon, thumbnailImage = self.url+images[i])

                link = common.parseDOM(buttons[i], "a", attrs = {"class":"download"}, ret="href")
                if link:
                    # TODO: move to separate function
                    if self.addon.getSetting('info') == "true":
                      response = common.fetchPage({"link": link[0]})["content"]
                      desc = common.parseDOM(response, "div", attrs = {"class":"description-text"})
                      description = common.stripTags(common.parseDOM(desc, "p")[1])

                      info = common.parseDOM(response, "div", attrs = {"class":"description"})
                      year = common.stripTags(common.parseDOM(info, "li")[1])

                      raiting = common.parseDOM(response, "div", attrs = {"class":"raiting"})

                      if raiting:
                        score = common.stripTags(common.parseDOM(raiting, "div", attrs = {"class":"value"})[0])
                      else:
                        score = ""

                      infos = {'title': title, 'genre': year+' IMBd: '+score, 'plot': description}

                    else:
                      infos = { "title": title }

                    uri = sys.argv[0] + '?mode=play&url=%s'%link[0] + '&category=%s'%category
                    item.setInfo( type='Video', infoLabels=infos)
                    item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

                else:
                    link = common.parseDOM(buttons[i], "a", attrs = {"class":"serialinfo"}, ret="href")
                    uri = sys.argv[0] + '?mode=season&url=%s'%link[0]
                    item.setInfo( type="Video", infoLabels={ "Title": title } )
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

            if len(titles) == 42:
              page = url + '/2' if url[-2:].find('/') == -1 else url[:-1] + str(int(url[-1])+1)
              uri = sys.argv[0] + '?mode=items&url=%s'%page
              item = xbmcgui.ListItem('Next page >>', iconImage = self.icon, thumbnailImage = self.icon)
              xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
              print page
        else:
            self.showErrorMessage("*** ERROR in getItems(), bad response status%s"%response["status"])

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

        
    def getSeasonsCatalog(self, url):
        response = common.fetchPage({"link": url})

        if response["status"] == 200:
            center = common.parseDOM(response["content"], "div", attrs = { "id":"center-colume" })
            content = common.parseDOM(center, "div", attrs = { "class":"content" })
            titles = common.parseDOM(content, "a", ret="title")
            links = common.parseDOM(content, "a", ret="href")

            for i,title in enumerate(titles):
                uri = sys.argv[0] + '?mode=season&url=%s'%links[i]
                item = xbmcgui.ListItem(title, iconImage = self.icon, thumbnailImage = self.icon)
                item.setInfo( type="Video", infoLabels={ "Title": title } )
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

            if len(links):
                page = url + '/page/2' if url.find("page") == -1 else url[:-1] + str(int(url[-1])+1)
                uri = sys.argv[0] + '?mode=seasons&url=%s'%page
                item = xbmcgui.ListItem('Next page >>', iconImage = self.icon, thumbnailImage = self.icon)
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("*** ERROR in index(), bad response status%s"%response["status"])

        xbmcplugin.endOfDirectory(self.handle, True)

    def getSeasonItems(self, url):
        response = common.fetchPage({"link": url})

        if response["status"] == 200:
            center = common.parseDOM(response["content"], "div", attrs = { "id":"center-colume" })
            epizode = common.parseDOM(center, "div", attrs = { "class":"epizode-list" })
            rows = common.parseDOM(epizode, "tr")

            for i,row in enumerate(rows):
                links = common.parseDOM(row, "a", ret="href")
                titles = common.parseDOM(row, "a", ret="title")

                if links and titles:
                    uri = sys.argv[0] + '?mode=play&url=%s'%links.pop(0)
                    
                    title = titles.pop(0).replace(self.language(5000).encode('utf-8'), '')
                    item = xbmcgui.ListItem(title, iconImage = self.icon, thumbnailImage = self.icon)
                    item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        else:
            self.showErrorMessage("*** ERROR in index(), bad response status%s"%response["status"])

        xbmcplugin.endOfDirectory(self.handle, True)


    def playItem(self, url):
        try:
            request = urllib2.Request(url)
            request.add_header('Referer', url)
            response = urllib2.urlopen(request, None) # timeout = 10?

            print response.geturl()
            print response.info()["Content-Type"]

            item = xbmcgui.ListItem(path = response.geturl())
            item.setProperty('mimetype', response.info()["Content-Type"])
            xbmcplugin.setResolvedUrl(self.handle, True, item)

        except:
            print "Unexpected error:", sys.exc_info()[0]
            return False

    def showErrorMessage(self, msg):
        print msg
        xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("ERROR",msg))  

    def addLink(name,url,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok


    def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

kinoboom = Kinoboom()
kinoboom.main()
