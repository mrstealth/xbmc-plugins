#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 2.0.1
# -*- coding: utf-8 -*-

import os, urllib, urllib2, sys, socket, cookielib, errno
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import json
import CommonFunctions
common = CommonFunctions

timeout = 5
socket.setdefaulttimeout(timeout)

import Translit as translit
translit = translit.Translit(encoding='cp1251')

class Uakino():
    def __init__(self):
        self.id = 'plugin.video.uakino.net'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])
        self.url = 'http://uakino.net'

        self.inext = os.path.join(self.path, 'resources/icons/next.png')


    def main(self):
        params = common.getParameters(sys.argv[2])
        mode = url = category = page = None
        title = image = genre = desc = None

        mode = params['mode'] if params.has_key('mode') else None
        url = urllib.unquote_plus(params['url']) if params.has_key('url') else None
        offset = params['offset'] if params.has_key('offset') else 0

        if mode == 'play':
            self.play(url)
        if mode == 'movie':
            self.getMovieURL(url)
        if mode == 'subcategory':
            self.getSubCategoryItems(url, offset)
        if mode == 'category':
            self.getCategoryItems(url)
        if mode == 'search':
            self.search()
        elif mode == None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&url=%s'%("search", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FF00][ %s ][/COLOR]"%self.language(1000), thumbnailImage = self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s'%("subcategory", urllib.quote_plus("http://uakino.net/category/video/137"))
        item = xbmcgui.ListItem(self.language(1003), thumbnailImage = self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
        
        self.getCategories()
        xbmcplugin.endOfDirectory(self.handle, True)
      
    def getCategories(self):
        url = 'http://uakino.net/video'
        response = common.fetchPage({"link": url})
        
        if response["status"] == 200:
            catalog_tree = common.parseDOM(response["content"], "div", attrs = { "class":"catalog_tree" })
            parents = common.parseDOM(catalog_tree, "li", attrs = {"class": "parent_closed"})
            paths = common.parseDOM(catalog_tree, "li", attrs = {"class": "parent_closed"}, ret="cid")

            titles = common.parseDOM(catalog_tree, "a", attrs = {"href": "javascript:"})

            for i, title in enumerate(titles):
                url = "%s/category/video/%s"%(self.url, paths[i])
                uri = sys.argv[0] + '?mode=category&url=%s'%url
                item = xbmcgui.ListItem(title, iconImage = self.icon, thumbnailImage = self.icon)
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status %s"%response["status"])
            
        xbmcplugin.endOfDirectory(self.handle, True)
    

    def getCategoryItems(self, url):
        print "*** get category items %s"%url
        response = common.fetchPage({"link": url})
        
        if response["status"] == 200:
            media_line = common.parseDOM(response["content"], "div", attrs = { "class":"tab media_line" })
            
            thumbs = common.parseDOM(media_line, "a", attrs = {"class": "fleft thumb"})
            links = common.parseDOM(media_line, "a", attrs = {"class": "fleft thumb"}, ret="href")

            images = common.parseDOM(thumbs, "img", ret="src")
            titles = common.parseDOM(thumbs, "img", ret="alt")
            
            for i, title in enumerate(titles):
                url = "%s/%s"%(self.url, links[i])
                uri = sys.argv[0] + '?mode=subcategory&url=%s'%url
                item = xbmcgui.ListItem(title, thumbnailImage = self.url+images[i], iconImage=self.icon)
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status %s"%response["status"])     
            
        xbmcplugin.endOfDirectory(self.handle, True)
           

    def getSubCategoryItems(self, url, offset):
        print "*** get subcategory items %s"%url
        
        if offset == 0:
            response = common.fetchPage({"link": url})
        else:
            response = common.fetchPage({"link": "%s?order=date&offset=%s"%(url, offset)})

        items_counter = 0
        
        if response["status"] == 200:
            media_line = common.parseDOM(response["content"], "div", attrs = { "class":"tab media_line" })
        
            titlesA = common.parseDOM(media_line, "a", ret="title")
            pathsA = common.parseDOM(media_line, "a", attrs = {"class":"fleft thumb"}, ret="href")
        
            titlesB = common.parseDOM(media_line, "a", attrs = {"class":"heading"})
            pathsB = common.parseDOM(media_line, "a", attrs = {"class":"heading"}, ret="href")
        
            images = common.parseDOM(media_line, "img", ret="src")
        
        
            print "Found A: %d"%len(titlesA)
            print "Found B: %d"%len(titlesB)
            
            print "Found images %d"%len(images)
            
            print images

            if titlesA and titlesB:
                print "*** This is a mix of seasons and movies"
                
                for i, title in enumerate(titlesA):
                    items_counter += 1
                    
                    link = "%s/%s"%(self.url, pathsA[i])
                    image = self.url+images[i] if images[i].find('http') == -1 else images[i]
                    
                    uri = sys.argv[0] + '?mode=subcategory&url=%s'%link
                    item = xbmcgui.ListItem(title, thumbnailImage = image, iconImage=self.icon)
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
        
                for i, title in enumerate(titlesB):
                    items_counter += 1

                    link = "%s/%s"%(self.url, pathsB[i])
                    image = self.url+images[len(titlesA)+i] if images[len(titlesA)+i].find('http') == -1 else images[len(titlesA)+i]
                    
                    uri = sys.argv[0] + '?mode=movie&url=%s'%link
                    item = xbmcgui.ListItem(title, thumbnailImage = image, iconImage=self.icon)
                    item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
        
            elif titlesA:
                print "*** This is a season"
        
                for i, title in enumerate(titlesA):
                    items_counter += 1

                    link = "%s/%s"%(self.url, pathsA[i])
                    image = self.url+images[i] if images[i].find('http') == -1 else images[i]

                    uri = sys.argv[0] + '?mode=subcategory&url=%s'%link
                    item = xbmcgui.ListItem(title, thumbnailImage = image, iconImage=self.icon)
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
    
    
            elif titlesB:
                print "*** This is a movie"
        
                ul = common.parseDOM(media_line, "ul")
        
                for i, title in enumerate(titlesB):
                    genres = common.stripTags(common.parseDOM(ul[i], "li")[0])
        
                    try:
                        description = common.stripTags(common.parseDOM(ul[i], "li")[2])
                    except IndexError:
                        description = common.stripTags(common.parseDOM(ul[i], "li")[1])

                    items_counter += 1
                    
                    link = "%s/%s"%(self.url, pathsA[i])
                    image = self.url+images[i] if images[i].find('http') == -1 else images[i]
                    info = {'title': title, 'genre': genres, 'plot': description}

                    uri = sys.argv[0] + '?mode=movie&url=%s'%link
                    item = xbmcgui.ListItem(title, thumbnailImage = image, iconImage=self.icon)
                    
                    item.setInfo( type='Video', infoLabels=info)        
                    item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
            else:
              print "Exception"
              
        else:
            self.showErrorMessage("getCategoryItems(): Bad response status %s"%response["status"])  


        if items_counter == 16:
            self.nextPage(url, offset)
            
        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)
                    

    def nextPage(self, url, offset):
        print "*** Next page %s and offset %s"%(url, offset)
        response = common.fetchPage({"link": url})
        
        navbar = common.parseDOM(response["content"], "div", attrs = { "class":"nav_buttons fright" })
        links = common.parseDOM(navbar, "a", attrs= {"class" : "nav_button"})
    
        if navbar and len(links) > 2:
            uri = sys.argv[0] + '?mode=subcategory&url=%s&offset=%s'%(url, str(int(offset)+16))
            item = xbmcgui.ListItem('Next page >>', thumbnailImage = self.icon, iconImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)


    def getMovieURL(self, url):
        print "*** get movie url for: %s"%url
        page = common.fetchPage({"link": url})
        path = common.parseDOM(page["content"], "a", attrs = { "id":"player" }, ret="href")[0]
        url = "%s/%s"%(self.url,path)
        self.play(url)
   

    def play(self, url):
        print "*** play url %s"%url
        item = xbmcgui.ListItem(path = url)
        xbmcplugin.setResolvedUrl(self.handle, True, item)         


    def search(self):

        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        kbd.setHeading(self.language(1000))
        kbd.doModal()
        keyword=''

        if kbd.isConfirmed():
            if self.addon.getSetting('translit') == 'true':
                keyword = translit.rus(kbd.getText())
            else:
                keyword = kbd.getText()

            url = 'http://uakino.net/search_result.php'

            headers = {
                "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip,deflate",
                "Accept-Language" : "en-US,en;q=0.5",
                "Connection" : "keep-alive",
                "Content-Type" : "application/x-www-form-urlencoded",
                "Host" : "	uakino.net",
                "Referer" : url,
                "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/17.0 Firefox/17.0"
            }
      
            values = {
                "search_id" : keyword,
                "send" : "%D0%9F%D0%BE%D0%B8%D1%81%D0%BA"
            }

            data = urllib.urlencode(values)
            req = urllib2.Request(url, data, headers)

            response = urllib2.urlopen(req)
            html = response.read()
            
            print self.encode(keyword)

            if html:
                media_line = common.parseDOM(html, "div", attrs = { "class":"media_line" })
            
                titlesA = common.parseDOM(media_line, "a", ret="title")
                pathsA = common.parseDOM(media_line, "a", attrs = {"class":"fleft thumb"}, ret="href")
            
                titlesB = common.parseDOM(media_line, "a", attrs = {"class":"heading"})
                pathsB = common.parseDOM(media_line, "a", attrs = {"class":"heading"}, ret="href")
            
                images = common.parseDOM(media_line, "img", ret="src")
            
                items_counter = 0
            
                print "Found A: %d"%len(pathsA)
                print "Found B: %d"%len(pathsB)
                print "Found images %d"%len(images)
    
                if titlesA and titlesB:
                    print "*** This is a mix of seasons and movies"
                    
                    for i, title in enumerate(titlesA):
                        items_counter += 1
                        
                        link = "%s/%s"%(self.url, pathsA[i])
                        image = self.url+images[i] if images[i].find('http') == -1 else images[i]
                        
                        uri = sys.argv[0] + '?mode=subcategory&url=%s'%link
                        item = xbmcgui.ListItem(title, thumbnailImage = image, iconImage=self.icon)
                        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
            
                    for i, title in enumerate(titlesB):
                        items_counter += 1
    
                        link = "%s/%s"%(self.url, pathsB[i])
                        image = self.url+images[len(pathsB)+i] if images[len(pathsB)+i].find('http') == -1 else images[len(pathsB)+i]
                        
                        uri = sys.argv[0] + '?mode=movie&url=%s'%link
                        item = xbmcgui.ListItem(title, thumbnailImage = image, iconImage=self.icon)
                        item.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
            
                elif titlesA:
                    print "*** This is a season"
            
                    for i, title in enumerate(titlesA):
                        items_counter += 1
    
                        link = "%s/%s"%(self.url, pathsA[i])
                        image = self.url+images[i] if images[i].find('http') == -1 else images[i]
    
                        uri = sys.argv[0] + '?mode=subcategory&url=%s'%link
                        item = xbmcgui.ListItem(title, thumbnailImage = image, iconImage=self.icon)
                        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
        
        
                elif titlesB:
                    print "*** This is a movie"
            
                    ul = common.parseDOM(media_line, "ul")
            
                    for i, title in enumerate(titlesB):
                        genres = common.stripTags(common.parseDOM(ul[i], "li")[0])
            
                        try:
                            description = common.stripTags(common.parseDOM(ul[i], "li")[2])
                        except IndexError:
                            description = common.stripTags(common.parseDOM(ul[i], "li")[1])
    
                        items_counter += 1
                        
                        link = "%s/%s"%(self.url, pathsA[i])
                        image = self.url+images[i] if images[i].find('http') == -1 else images[i]
                        info = {'title': title, 'genre': genres, 'plot': description}
    
                        uri = sys.argv[0] + '?mode=movie&url=%s'%link
                        item = xbmcgui.ListItem(title, thumbnailImage = image, iconImage=self.icon)
                        
                        item.setInfo( type='Video', infoLabels=info)        
                        item.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
                else:
                    item = xbmcgui.ListItem(self.language(9001), thumbnailImage = self.icon)
                    xbmcplugin.addDirectoryItem(self.handle, "", item, False)                  
            else:
                self.showErrorMessage("search(): Bad response status %s"%response["status"])  
    
            xbmc.executebuiltin('Container.SetViewMode(52)')
            xbmcplugin.endOfDirectory(self.handle, True)


        else:
            self.menu()

        xbmcplugin.endOfDirectory(self.handle, True)
            
               
    # HELPERS
    def showErrorMessage(self, msg):
        print msg
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)"%("ERROR",msg, str(10*1000)))

    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')
      
uakino = Uakino()
uakino.main()