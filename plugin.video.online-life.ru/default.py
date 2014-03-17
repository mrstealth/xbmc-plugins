#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 2.1.3
# -*- coding: utf-8 -*-

import os
import urllib
import urllib2
import sys
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import re
import XbmcHelpers
common = XbmcHelpers

import Translit as translit
translit = translit.Translit(encoding='cp1251')

# UnifiedSearch module
try:
    sys.path.append(os.path.dirname(__file__)+ '/../plugin.video.unified.search')
    from unified_search import UnifiedSearch
except: pass

# My Favorites module
from MyFavorites import MyFavorites

# YouTube module
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

# Exception => Dieses Video enthaelt Content von CTB Film Company. Es darf auf bestimmten Websites nicht wiedergegeben werden
#from youtube_module import YoutubeModule
#from youtube_module import YoutubeModuleException
#youtube = YoutubeModule()


from pytube import YouTube
yt = YouTube()

class URLParser():
    def parse(self, string):
        links = re.findall(r'(?:http://|www.).*?["]', string)
        return list(set(self.filter(links)))

    def filter(self, links):
        links = self.strip(links)
        return [l for l in links if l.endswith('.mp4') or l.endswith('.mp4') or l.endswith('.txt')]

    def strip(self, links):
        return [l.replace('"', '') for l in links]


class OnlineLife():
    def __init__(self):
        self.id = 'plugin.video.online-life.ru'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])
        self.url = 'http://www.online-life.ru'

        self.favorites = MyFavorites(self.id)

        self.inext = os.path.join(self.path, 'resources/icons/next.png')
        self.debug = False

    def main(self):
        params = common.getParameters(sys.argv[2])
        mode = url = page = None

        mode = params['mode'] if 'mode' in params else None
        url = urllib.unquote_plus(params['url']) if 'url' in params else None
        page = params['page'] if 'page' in params else 1

        keyword = params['keyword'] if 'keyword' in params else None
        unified = params['unified'] if 'unified' in params else None

        if mode == 'play':
            self.play(url)
        if mode == 'search':
            self.search(keyword, unified)
        if mode == 'genres':
            self.listGenres(url)
        if mode == 'show':
            self.getFilmInfo(url)
        if mode == 'category':
            self.getCategoryItems(url, page)
        if mode == 'favorites':
            self.show_favorites()
        elif mode is None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        item = xbmcgui.ListItem("[B][COLOR=FF00FF00]%s[/COLOR][/B]" % self.language(2000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.favorites.ListItem()

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("genres", self.url)
        item = xbmcgui.ListItem("[B][COLOR=FF00FFF0]%s[/COLOR][/B]" % self.language(1000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("category", "http://www.online-life.ru/kino-multserial/")
        item = xbmcgui.ListItem("[B][COLOR=FF00FFF0]%s[/COLOR][/B]" % self.language(1004), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.getCategoryItems(self.url, 0)
        xbmcplugin.endOfDirectory(self.handle, True)

    def getCategoryItems(self, url, page):
        page_url = self.url if page == 0 else "%s/page/%s/" % (url, str(int(page)))
        response = common.fetchPage({"link": page_url})

        if response["status"] == 200:
            container = common.parseDOM(response["content"], "div", attrs={"id": "container"})
            posts = common.parseDOM(container, "div", attrs={"class": "custom-post media-grid"})
            extras = common.parseDOM(container, "div", attrs={"class": "extra"})
            pagenav = common.parseDOM(container, "div", attrs={"class": "navigation"})

            ratings = common.parseDOM(container, "li", attrs={"class": "current-rating"})
            items = 0

            for i, post in enumerate(posts):
                items += 1

                poster = common.parseDOM(post, "div", attrs={"class": "custom-poster"})
                media_data = common.parseDOM(extras[i], "div", attrs={"class": "media-data text-overflow"})

                title = self.encode(common.stripTags(common.parseDOM(poster, "a")[0]))
                link = common.parseDOM(poster, "a", ret="href")[0]
                image = common.parseDOM(poster, "img", ret="src")[0]

                description = self.encode(common.stripTags(common.parseDOM(extras[i], "div", attrs={"class": "description"})[0]))
                genres = self.encode(', '.join(common.parseDOM(media_data, "a")))

                rating = float(ratings[i]) / 10

                uri = sys.argv[0] + '?mode=show&url=%s' % link
                item = xbmcgui.ListItem(title, thumbnailImage=image)
                item.setInfo(type='Video', infoLabels={'title': title, 'genre': genres, 'plot': description, 'rating': rating})

                self.favorites.addContextMenuItem(item, {'title': title, 'url': link, 'image': image, 'playable': False, 'action': 'add', 'plugin': self.id})

                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

            if pagenav and not items < 20:
                uri = sys.argv[0] + '?mode=%s&url=%s&page=%s' % ("category", url, str(int(page) + 1))
                item = xbmcgui.ListItem(self.language(9001), thumbnailImage=self.inext)
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("getCategoryItems(): Bad response status%s" % response["status"])

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def getFilmInfo(self, url):
        response = common.fetchPage({"link": url})

        content = common.parseDOM(response["content"], "div", attrs={"id": "dle-content"})
        story = common.parseDOM(response["content"], "div", attrs={"class": "full-story"})

        title = self.encode(common.parseDOM(story, "span", attrs={"itemprop": "name"})[0])
        image = common.parseDOM(story, "img", attrs={"itemprop": "image"}, ret="src")[0]

        scripts = common.parseDOM(content, "script", attrs={"type": "text/javascript"})

        itemprop_genre = common.parseDOM(story, "span", attrs={"itemprop": "genre"})
        genres = self.encode(', '.join(common.parseDOM(itemprop_genre, 'a')))

        desc = self.encode(common.parseDOM(story, "div", attrs={"style": "display:inline;"})[0])

        parser = URLParser()

        #for i, script in enumerate(scripts):
        #    print "%d #########" % i
        #    print script

        try:
            link = parser.parse(scripts[6])[0]
        except IndexError:
            link = parser.parse(scripts[7])[0]

        movie = link if not link.endswith('.txt') else None
        season = link if link.endswith('.txt') else None

        if movie:
            uri = sys.argv[0] + '?mode=play&url=%s' % urllib.quote_plus(movie)

            item = xbmcgui.ListItem(title, thumbnailImage=image)
            item.setInfo(type='Video', infoLabels={'title': title, 'genre': genres, 'plot': common.stripTags(desc), 'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0})
            item.setProperty('IsPlayable', 'true')

            xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
            xbmc.executebuiltin('Container.SetViewMode(52)')

        elif season:
            print "This is a season %s" % season
            response = common.fetchPage({"link": season})

            if response["status"] == 200:
                response = eval(response["content"].replace('\t', '').replace('\r\n', ''))

                if 'playlist' in response['playlist'][0]:
                    print "This is a season multiple seasons"

                    for season in response['playlist']:
                        episods = season['playlist']

                        for episode in episods:
                            etitle = "%s (%s)" % (episode['comment'], common.stripTags(season['comment']))
                            url = episode['file']

                            # print "**** %s" % url

                            uri = sys.argv[0] + '?mode=play&url=%s' % urllib.quote_plus(url)
                            item = xbmcgui.ListItem(etitle, thumbnailImage=image)

                            labels = {'title': title, 'genre': 'genre', 'plot': 'desc', 'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0}
                            item.setInfo(type='Video', infoLabels=labels)

                            item.setProperty('IsPlayable', 'true')
                            xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
                    xbmc.executebuiltin('Container.SetViewMode(51)')

                else:
                    print "This is one season"
                    for episode in response['playlist']:
                        etitle = episode['comment']
                        url = episode['file']

                        uri = sys.argv[0] + '?mode=play&url=%s' % urllib.quote_plus(url)
                        item = xbmcgui.ListItem(etitle, thumbnailImage=image)

                        labels = {'title': title, 'genre': 'genre', 'plot': 'desc', 'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0}

                        item.setInfo(type='Video', infoLabels=labels)
                        item.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
                    xbmc.executebuiltin('Container.SetViewMode(51)')

        xbmcplugin.endOfDirectory(self.handle, True)

    def listGenres(self, url):
        response = common.fetchPage({"link": url})

        container = common.parseDOM(response["content"], "div", attrs={"class": "nav"})
        titles = common.parseDOM(container, "a", attrs={"class": "link1"})
        links = common.parseDOM(container, "a", attrs={"class": "link1"}, ret="href")

        uri = sys.argv[0] + '?mode=category&url=%s' % "http://www.online-life.ru/kino-new/"
        item = xbmcgui.ListItem(self.language(1007), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        for i, title in enumerate(titles):
            link = links[i] if links[i].startswith('http') else self.url + links[i]
            uri = sys.argv[0] + '?mode=category&url=%s' % link
            item = xbmcgui.ListItem(self.encode(title), thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=category&url=%s' % "http://www.online-life.ru/kino-tv/"
        item = xbmcgui.ListItem(self.language(1006), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmcplugin.endOfDirectory(self.handle, True)

    def show_favorites(self):
        self.favorites.list()
        xbmcplugin.endOfDirectory(self.handle, True)

    def play(self, url):
        print "Play media URL: %s" % url

        hd = True if  self.addon.getSetting('hd_youtube_videos') == 'true' else False
        supported_resolutions = ['720p', '1080p'] if hd else ['360p', '480p']
        video_url = ''

        try:
            if 'youtube' in url:
                # url =  youtube.get_youtube_url(url, hd) if 'youtube' in url else url
                yt.url = url
                video_url = yt.videos[-1].url
                # for video in yt.videos:
                #     extension = video.__dict__['extension']
                #     resolution = video.__dict__['resolution']

                #     if resolution in supported_resolutions and extension == 'mp4':
                #         # print "%s %s" % (video.extension, video.resolution)
                #         video_url = yt.videos[0].url
                #     else:
                #         print "Unsupported resolution or video format: %s %s" % (resolution, extension)
            else:
                video_url = url

            print urllib.unquote(video_url)
            item = xbmcgui.ListItem(path=video_url)
            xbmcplugin.setResolvedUrl(self.handle, True, item)
        except Exception, e:
            self.showErrorMessage(e)

    def getUserInput(self):
        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        kbd.setHeading(self.language(4000))
        kbd.doModal()
        keyword = None

        if kbd.isConfirmed():
            if self.addon.getSetting('translit') == 'true':
                keyword = translit.rus(kbd.getText())
            else:
                keyword = kbd.getText()
        return keyword

    def search(self, keyword, unified):
        self.log("*** Search: unified %s" % unified)

        keyword = translit.rus(keyword) if unified else self.getUserInput()
        unified_search_results = []

        if keyword:
            url = 'http://www.online-life.ru/index.php?do=search'

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

            container = common.parseDOM(response, "div", attrs={"id": "container"})
            posts = common.parseDOM(container, "div", attrs={"class": "custom-post"})

            if unified:
                self.log("Perform unified search and return results")

                for i, post in enumerate(posts):
                    poster = common.parseDOM(post, "div", attrs={"class": "custom-poster"})
                    title = self.encode(common.stripTags(common.parseDOM(post, "a")[0]))
                    link = common.parseDOM(post, "a", ret="href")[0]
                    image = common.parseDOM(post, "img", ret="src")[0]


                    unified_search_results.append({'title':  title, 'url': link, 'image': image, 'plugin': self.id})

                UnifiedSearch().collect(unified_search_results)

            else:
                if posts:
                    for i, post in enumerate(posts):
                        poster = common.parseDOM(post, "div", attrs={"class": "custom-poster"})
                        title = self.encode(common.stripTags(common.parseDOM(post, "a")[0]))
                        link = common.parseDOM(post, "a", ret="href")[0]
                        image = common.parseDOM(post, "img", ret="src")[0]

                        uri = sys.argv[0] + '?mode=show&url=%s' % link
                        item = xbmcgui.ListItem(title, thumbnailImage=image)

                        self.favorites.addContextMenuItem(item, {
                            'title': title,
                            'url': link,
                            'image': image,
                            'playable': False,
                            'action': 'add',
                            'plugin': self.id
                        })

                        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

                    xbmc.executebuiltin('Container.SetViewMode(52)')
                else:
                    item = xbmcgui.ListItem(self.language(2001), iconImage=self.icon, thumbnailImage=self.icon)
                    xbmcplugin.addDirectoryItem(self.handle, '', item, True)

                xbmcplugin.endOfDirectory(self.handle, True)
        else:
            self.menu()

    # === Addon helpers
    def log(self, message):
        if self.debug:
            print "### %s: %s" % (self.id, message)

    def error(self, message):
        print "%s ERROR: %s" % (self.id, message)

    def isCyrillic(self, keyword):
        if not re.findall(u"[\u0400-\u0500]+", keyword):
            return False
        else:
            return True

    def showErrorMessage(self, msg):
        print msg
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("ERROR", msg, str(10 * 1000)))

    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')

plugin = OnlineLife()
plugin.main()
