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
# Rev. 1.0.1

import os, urllib, urllib2, sys #, socket, cookielib, errno
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import re, json

import XbmcHelpers
common = XbmcHelpers

import Translit as translit
translit = translit.Translit(encoding='cp1251')


class HdrezkaTV():
    def __init__(self):
        self.id = 'plugin.video.hdrezka.tv'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.fanart = self.addon.getAddonInfo('fanart')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.inext = os.path.join(self.path, 'resources/icons/next.png')
        self.handle = int(sys.argv[1])
        self.url = 'http://hdrezka.tv'

    def main(self):
        params = common.getParameters(sys.argv[2])
        mode = url = page = None

        mode = params['mode'] if 'mode' in params else None
        url = urllib.unquote_plus(params['url']) if 'url' in params else None
        page = int(params['page']) if 'page' in params else 1

        post_id = params['post_id'] if 'post_id' in params else None
        season_id = params['season_id'] if 'season_id' in params else None
        episode_id = params['episode_id'] if 'episode_id' in params else None

        keyword = params['keyword'] if 'keyword' in params else None
        unified = params['unified'] if 'unified' in params else None

        if mode == 'play':
            self.play(url)
        if mode == 'play_episode':
            self.play_episode(url, post_id, season_id, episode_id)
        if mode == 'show':
            self.show(url)
        if mode == 'index':
            self.index(url, page)
        if mode == 'categories':
            self.categories()
        if mode == 'search':
            self.search(keyword, unified)
        elif mode == None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FF00][%s][/COLOR]" % self.language(1000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("categories", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(1003), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.index('http://hdrezka.tv/films', 1)
        xbmcplugin.endOfDirectory(self.handle, True)

    def categories(self):
        response = common.fetchPage({"link": self.url})
        genres = common.parseDOM(response["content"], "ul", attrs={"id": "topnav-menu"})

        titles = common.parseDOM(genres, "a", attrs={"class": "b-topnav__item-link"})
        links = common.parseDOM(genres, "a", attrs={"class": "b-topnav__item-link"}, ret='href')

        for i, title in enumerate(titles):
            title = common.stripTags(title)
            link = self.url + links[i]

            uri = sys.argv[0] + '?mode=%s&url=%s' % ("index", link)
            item = xbmcgui.ListItem(title, thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)


        xbmcplugin.endOfDirectory(self.handle, True)

    def sub_categories(self, category_id):
        response = common.fetchPage({"link": self.url})
        genres = common.parseDOM(response["content"], "ul", attrs={"id": "topnav-menu"})

        titles = common.parseDOM(genres, "a")
        links = common.parseDOM(genres, "a", ret='href')

        for i, title in enumerate(titles):
            if 'http' in links[i]:
                link = links[i]
            else:
                link = self.url + links[i]

            uri = sys.argv[0] + '?mode=%s&url=%s' % ("index", link)
            item = xbmcgui.ListItem(title, thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)


        xbmcplugin.endOfDirectory(self.handle, True)


    def index(self, url, page):
        if(page == 1):
            page_url = url
        else:
            page_url = "%s/page/%s/" % (url, page)

        print page_url

        response = common.fetchPage({"link": page_url})
        content = common.parseDOM(response["content"], "div", attrs={"class": "b-content__inline_items"})
        items = common.parseDOM(content, "div", attrs={"class": "b-content__inline_item"})
        post_ids = common.parseDOM(content, "div", attrs={"class": "b-content__inline_item"}, ret="data-id")

        link_containers = common.parseDOM(items, "div", attrs={"class": "b-content__inline_item-link"})

        links = common.parseDOM(link_containers, "a", ret='href')
        titles = common.parseDOM(link_containers, "a")
        images = common.parseDOM(items, "img", ret='src')

        country_years = common.parseDOM(link_containers, "div")
        items_count = 0

        print len(titles)
        print len(images)
        print len(country_years)

        for i, title in enumerate(titles):
            items_count += 1

            # print post_ids[i]
            infos = self.get_item_description(url, post_ids[i])

            country_year = country_years[i].split(',')[0].replace('.', '').replace('-', '').replace(' ', '')
            title = "%s [COLOR=55FFFFFF](%s)[/COLOR]" % (title, country_year)
            image = self.url+images[i]

            uri = sys.argv[0] + '?mode=show&url=%s' % links[i]
            item = xbmcgui.ListItem(title, iconImage=image)
            item.setInfo(type='Video', infoLabels={'title': title, 'genre': country_years[i], 'plot': infos['description'], 'rating': infos['rating']})
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        if not items_count < 16:
            uri = sys.argv[0] + '?mode=%s&url=%s&page=%s' % ("index", url, str(int(page) + 1))
            item = xbmcgui.ListItem(self.language(1004), iconImage=self.inext)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def show(self, url):
        print "Get video %s" % url
        response = common.fetchPage({"link": url})

        content = common.parseDOM(response["content"], "div", attrs={"id": "wrapper"})
        image_container = common.parseDOM(content, "div", attrs={"class": "b-sidecover"})

        title = common.parseDOM(content, "h1")[0]
        image = common.parseDOM(image_container, "img", ret='src')[0]

        playlist = common.parseDOM(content, "ul", attrs={"class": "b-simple_episodes__list clearfix"})
        post_id = common.parseDOM(content, "input", attrs={"id": "post_id" }, ret="value")[0]

        titles = common.parseDOM(playlist, "li")
        ids = common.parseDOM(playlist, "li", ret='data-id')
        seasons = common.parseDOM(playlist, "li", ret='data-season_id')
        episodes = common.parseDOM(playlist, "li", ret='data-episode_id')

        print playlist
        print "POST ID %s " % post_id
        print "Image %s" % image

        if playlist:
            print "This is a season"
            for i, title in enumerate(titles):
                title = "%s (%s %s)" % (title, self.language(1005), seasons[i])

                uri = sys.argv[0] + '?mode=play_episode&url=%s&post_id=%s&season_id=%s&episode_id=%s' % (url, ids[i], seasons[i], episodes[i])
                item = xbmcgui.ListItem(title, iconImage=image)
                item.setInfo(type='Video', infoLabels={'title': title, 'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0})
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        else:
            try:
                link = self.get_video_link(url, post_id)

                uri = sys.argv[0] + '?mode=play&url=%s' % urllib.quote(link)
                item = xbmcgui.ListItem(title, iconImage=image)
                item.setInfo(type='Video', infoLabels={'title': title, 'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0})
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

            except ValueError:
                print "GET LINK FROM IFRAME"
                videoplayer = common.parseDOM(content, 'div', attrs={'id': 'videoplayer'})
                iframe = common.parseDOM(content, 'iframe', ret='src')[0]
                links = self.get_video_link_from_iframe(iframe)

                # scripts = common.parseDOM(response["content"], "script")
                # scripts = scripts[4].split('<script>')
                # link = None

                # for i, script in enumerate(scripts):
                #     if 'index.m3u8' in script:
                #         print script
                #         link =  script.split('"hls":')[-1].split(',')[0].replace('\\', '').replace('"', '')


                print links

                for quality, link in links.iteritems():
                    print "quality: %s link %s" % (quality, link)
                    film_title = "%s (%s)" % (title, quality)

                    uri = sys.argv[0] + '?mode=play&url=%s' % urllib.quote(link)
                    item = xbmcgui.ListItem(film_title, iconImage=image)
                    item.setInfo(type='Video', infoLabels={'title': film_title, 'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0})
                    item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        xbmcplugin.endOfDirectory(self.handle, True)


    def get_item_description(self, referer, post_id):
        url = 'http://hdrezka.tv/engine/ajax/quick_content.php'

        headers = {
            "Accept" : "text/plain, */*; q=0.01",
            "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
            "Host" : "hdrezka.tv",
            "Referer" : referer,
            "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:27.0) Gecko/20100101 Firefox/27.0",
            "X-Requested-With" : "XMLHttpRequest"
        }

        data = urllib.urlencode({
            "id" : post_id,
            "is_touch" : 0
        })

        request = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(request).read()

        description = common.parseDOM(response, 'div', attrs={'class': 'b-content__bubble_text'})[0]

        try:
            imbd_rating = common.parseDOM(response, 'span', attrs={'class': 'imdb'})[0]
            rating = common.parseDOM(imbd_rating, 'b')[0]
        except IndexError, e:
            try:
                imbd_rating = common.parseDOM(response, 'span', attrs={'class': 'kp'})[0]
                rating = common.parseDOM(imbd_rating, 'b')[0]
            except IndexError, e:
                rating = 0

        return { 'rating' : rating, 'description' : description }

    def get_video_link_from_iframe(self, url):
        response = common.fetchPage({"link": url})['content']

        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', response)
        links = []
        manifest_links = {}

        for url in urls:
            if 'mp4' in url:
                links.append(url)

        for link in links:
            if 'manifest' in link:
                if '360' in link:
                    manifest_links['360p'] = link.replace("',", '').replace("manifest.f4m", 'index.m3u8')
                elif '480':
                    manifest_links['480p'] = link.replace("',", '').replace("manifest.f4m", 'index.m3u8')
                elif '720':
                    manifest_links['720p'] = link.replace("',", '').replace("manifest.f4m", 'index.m3u8')

        return manifest_links

    def get_video_link(self, referer, post_id):
        url = 'http://hdrezka.tv/engine/ajax/getvideo.php'

        headers = {
            "Accept" : "text/plain, */*; q=0.01",
            "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
            "Host" : "hdrezka.tv",
            "Referer" : referer,
            "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:27.0) Gecko/20100101 Firefox/27.0",
            "X-Requested-With" : "XMLHttpRequest"
        }

        data = urllib.urlencode({
            "id" : post_id
        })

        request = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(request)

        response = json.loads(response.read().encode("utf-8"))
        links = json.loads(response['link'].encode("utf-8"))
        return links['hls']

    def get_seaons_link(self, referer, video_id, season, episode):
        url = 'http://hdrezka.tv/engine/ajax/getvideo.php'

        headers = {
            "Accept" : "text/plain, */*; q=0.01",
            "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
            "Host" : "hdrezka.tv",
            "Referer" : referer,
            "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:27.0) Gecko/20100101 Firefox/27.0",
            "X-Requested-With" : "XMLHttpRequest"
        }

        data = urllib.urlencode({
            'id': video_id,
            'season':  season,
            'episode': episode
        })

        request = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(request)

        response = json.loads(response.read().encode("utf-8"))
        links = json.loads(response['link'].encode("utf-8"))
        return links['hls']

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
        print "*** Search: unified %s" % unified

        keyword = translit.rus(keyword) if unified else self.getUserInput()
        unified_search_results = []

        if keyword:
            keyword = self.encode(keyword)

            print keyword

            url = 'http://www.videokub.com/search/?q=%s' % (keyword)

            response = urllib2.urlopen(url)

            content = common.parseDOM(response.read(), "div", attrs={"class": "list_videos"})
            videos = common.parseDOM(content, "div", attrs={"class": "short"})

            links = common.parseDOM(videos, "a", attrs={"class": "kt_imgrc"}, ret='href')
            titles = common.parseDOM(videos, "a", attrs={"class": "kt_imgrc"}, ret='title')
            images = common.parseDOM(videos, "img", attrs={"class": "thumb"}, ret='src')

            durations = common.parseDOM(videos, "span", attrs={"class": "time"})

            if unified:
                print "Perform unified search and return results"

                for i, title in enumerate(titles):
                    title = self.encode(title)
                    unified_search_results.append({'title':  title, 'url': links[i], 'image': self.url + images[i], 'plugin': self.id})

                UnifiedSearch().collect(unified_search_results)

            else:
                for i, title in enumerate(titles):
                    duration = durations[i].split(':')[0]

                    link = '88.150.243.226/vod/Skhvatka.1995.mp4/playlist.m3u8?token=3c076648ea987c21cf58a970f47fa4a5'

                    uri = sys.argv[0] + '?mode=show&url=%s' % urllib.quote(links[i])
                    item = xbmcgui.ListItem("%s [COLOR=55FFFFFF](%s)[/COLOR]" % (title, durations[i]), iconImage=images[i])
                    item.setInfo(type='Video', infoLabels={'title': title, 'genre': durations[i], 'duration': duration})
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

                xbmc.executebuiltin('Container.SetViewMode(52)')
                xbmcplugin.endOfDirectory(self.handle, True)

        else:
            self.menu()

    def play(self, url):
        item = xbmcgui.ListItem(path = url)
        xbmcplugin.setResolvedUrl(self.handle, True, item)

    def play_episode(self, referer, post_id, season_id, episode_id):
        print "***** play_season"
        url = self.get_seaons_link(referer, post_id, season_id, episode_id)

        print url
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

plugin = HdrezkaTV()
plugin.main()
