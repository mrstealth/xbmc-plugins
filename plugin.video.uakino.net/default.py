#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 2.0.9
# -*- coding: utf-8 -*-

import os, urllib, urllib2, sys, socket, re
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import uppod
import XbmcHelpers
common = XbmcHelpers

import Translit as translit
translit = translit.Translit(encoding='cp1251')

try:
    sys.path.append(os.path.dirname(__file__)+ '/../plugin.video.unified.search')
    from unified_search import UnifiedSearch
except:
    pass


class URLParser():
    def parse(self, string):
        links = re.findall(r'(?:http://|www.).*?["]', string)
        return list(set(self.filter(links)))

    def filter(self, links):
        links = self.strip(links)
        return [l for l in links if l.endswith('.mp4') or l.endswith('.mp4') or l.endswith('.txt')]

    def strip(self, links):
        return [l.replace('"', '') for l in links]

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
        self.debug = self.addon.getSetting("debug") == 'true'

    def main(self):
        params = common.getParameters(sys.argv[2])
        mode = url  = None

        mode = params['mode'] if params.has_key('mode') else None
        url = urllib.unquote_plus(params['url']) if params.has_key('url') else None
        offset = params['offset'] if params.has_key('offset') else 0

        keyword = params['keyword'] if 'keyword' in params else None
        unified = params['unified'] if 'unified' in params else None

        if mode == 'play':
            self.play(url)
        if mode == 'movie' or mode == 'show':
            self.getMovieURL(url)
        if mode == 'subcategory':
            self.getSubCategoryItems(url, offset)
        if mode == 'category':
            self.getCategoryItems(url)
        if mode == 'search':
            self.search(keyword, unified)
        elif mode == None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&url=%s'%("search", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FF00]%s[/COLOR]"%self.language(1000), thumbnailImage = self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.getCategories()
        xbmcplugin.endOfDirectory(self.handle, True)

    def getCategories(self):
        url = 'http://uakino.net/video'
        response = common.fetchPage({"link": url})

        if response["status"] == 200:
            catalog_tree = common.parseDOM(response["content"], "div", attrs = { "class":"footer" })
            blocks = common.parseDOM(catalog_tree, "div", attrs = { "class":"block" })
            paths = common.parseDOM(blocks[0], "li")

            titles = common.parseDOM(paths, "a")
            links = common.parseDOM(paths, "a", ret="href")

            for i, title in enumerate(titles):
                url = self.url + links[i]
                uri = sys.argv[0] + '?mode=subcategory&url=%s'%url
                item = xbmcgui.ListItem(title.replace(':', ''), iconImage = self.icon, thumbnailImage = self.icon)
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status %s"%response["status"])

        xbmc.executebuiltin('Container.SetViewMode(50)')
        xbmcplugin.endOfDirectory(self.handle, True)


    def getCategoryItems(self, url):
        self.log("*** Get category items %s" % url)
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
        self.log("*** Get subcategory items %s" % url)

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


            # print "Found A: %d"%len(titlesA)
            # print "Found B: %d"%len(titlesB)
            # print "Found images %d"%len(images)


            if titlesA and titlesB:
                self.log("*** This is a mix of seasons and movies")

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
                self.log("*** This is a season")

                for i, title in enumerate(titlesA):
                    items_counter += 1

                    link = "%s/%s"%(self.url, pathsA[i])
                    image = self.url+images[i] if images[i].find('http') == -1 else images[i]

                    uri = sys.argv[0] + '?mode=subcategory&url=%s'%link
                    item = xbmcgui.ListItem(title, thumbnailImage = image, iconImage=self.icon)
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)


            elif titlesB:
                self.log("*** This is a movie")

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
        self.log("Next page %s and offset %s"%(url, offset))
        response = common.fetchPage({"link": url})

        navbar = common.parseDOM(response["content"], "div", attrs = { "class":"nav_buttons fright" })
        links = common.parseDOM(navbar, "a", attrs= {"class" : "nav_button"})

        if navbar and len(links) > 2:
            uri = sys.argv[0] + '?mode=subcategory&url=%s&offset=%s'%(url, str(int(offset)+16))
            item = xbmcgui.ListItem(self.language(9002), thumbnailImage = self.icon, iconImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)


    def getMovieURL(self, url):
        self.log("Get iframe URL for: %s" % url)
        page = common.fetchPage({"link": url})
        media_div = common.parseDOM(page['content'], "div", attrs = {'class': 'media_details_embed'})
        iframe = media_div[0].replace('&lt;', '<').replace('&gt;', '>')
        iframe_url = common.parseDOM(iframe, 'iframe', ret='src')[0].replace('&quot;', '')

        self.log("Get media URL for: %s" % iframe_url)
        page = common.fetchPage({"link": iframe_url})
        links = []

        try:
            links = URLParser().parse(page['content'])
            url = None

            for link in links:
                if 'mp4' in link:
                    url = link

            if url:
                self.play(url)
            else:
                print "content %s" % content
                scripts = common.parseDOM(content, "script", attrs = {'type': 'text/javascript'})
                print "scripts %s" % scripts

                for script in scripts:
                    print script
                    links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', script)

                for link in links:
                    if 'mp4' in link:
                        url = link

        except IndexError:
            print "EXCEPTION: Media source not found"

    def play(self, url):
        self.log("Play video URL")
        self.log(url)

        item = xbmcgui.ListItem(path = url)
        xbmcplugin.setResolvedUrl(self.handle, True, item)

    def getUserInput(self):
        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        kbd.setHeading(self.language(1000))
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
            keyword = self.encode(keyword)

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
            html = None

            try:
                response = urllib2.urlopen(req)
                html = response.read()
            except  Exception:
                if unified:
                    UnifiedSearch().collect(unified_search_results)
                pass

            self.log(keyword)

            us_titles = []
            us_links = []
            us_images = []

            if html:
                media_line = common.parseDOM(html, "div", attrs = { "class":"media_line" })

                titlesA = common.parseDOM(media_line, "a", ret="title")
                pathsA = common.parseDOM(media_line, "a", attrs = {"class":"fleft thumb"}, ret="href")

                titlesB = common.parseDOM(media_line, "a", attrs = {"class":"heading"})
                pathsB = common.parseDOM(media_line, "a", attrs = {"class":"heading"}, ret="href")

                images = common.parseDOM(media_line, "img", ret="src")

                items_counter = 0

                # print "Found A: %d"%len(pathsA)
                # print "Found B: %d"%len(pathsB)
                # print "Found images %d"%len(images)

                if titlesA and titlesB:
                    print "*** This is a mix of seasons and movies"

                    for i, title in enumerate(titlesA):
                        items_counter += 1

                        link = "%s/%s"%(self.url, pathsA[i])
                        image = self.url+images[i] if not 'http' in images[i] else images[i]

                        # INFO: Collect search results
                        us_titles.append(title)
                        us_links.append(link)
                        us_images.append(image)

                        uri = sys.argv[0] + '?mode=subcategory&url=%s'%link
                        item = xbmcgui.ListItem(title, thumbnailImage = image, iconImage=self.icon)
                        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

                    for i, title in enumerate(titlesB):
                        items_counter += 1

                        link = "%s/%s"%(self.url, pathsB[i])
                        image = self.url+images[len(pathsB)+i] if not 'http' in images[len(pathsB)+i] else images[len(pathsB)+i]

                        # INFO: Collect search results
                        us_titles.append(title)
                        us_links.append(link)
                        us_images.append(image)

                        uri = sys.argv[0] + '?mode=movie&url=%s'%link
                        item = xbmcgui.ListItem(title, thumbnailImage = image, iconImage=self.icon)
                        item.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

                elif titlesA:
                    print "*** This is a season"

                    for i, title in enumerate(titlesA):
                        items_counter += 1

                        link = "%s/%s"%(self.url, pathsA[i])
                        image = self.url+images[i] if not 'http' in images[i] else images[i]

                        # INFO: Collect search results
                        us_titles.append(title)
                        us_links.append(link)
                        us_images.append(image)

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
                        image = self.url+images[i] if not 'http' in images[i] else images[i]
                        info = {'title': title, 'genre': genres, 'plot': description}

                        # INFO: Collect search results
                        us_titles.append(title)
                        us_links.append(link)
                        us_images.append(image)

                        uri = sys.argv[0] + '?mode=movie&url=%s'%link
                        item = xbmcgui.ListItem(title, thumbnailImage = image, iconImage=self.icon)

                        item.setInfo( type='Video', infoLabels=info)
                        item.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
                else:
                    item = xbmcgui.ListItem(self.language(9001), thumbnailImage = self.icon)
                    xbmcplugin.addDirectoryItem(self.handle, "", item, False)
            else:
                self.showErrorMessage("%s: Request timeout" % self.id)

            # INFO: Convert and send unified search results
            if unified:
                self.log("Perform unified search and return results")
                for i, title in enumerate(us_titles):
                    unified_search_results.append({'title':  title, 'url': us_links[i], 'image': us_images[i], 'plugin': self.id, 'is_playable': True})

                UnifiedSearch().collect(unified_search_results)
            else:
                xbmc.executebuiltin('Container.SetViewMode(50)')
                xbmcplugin.endOfDirectory(self.handle, True)

        else:
            self.menu()


    # ===== HELPERS
    def log(self, message):
        if self.debug:
            print "%s: %s" % (self.id, message)

    def error(self, message):
        print "%s ERROR: %s" % (self.id, message)

    def showErrorMessage(self, msg):
        print msg
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)"%("ERROR",msg, str(10*1000)))

    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')

uakino = Uakino()
uakino.main()
