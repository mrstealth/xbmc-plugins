#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.3
# -*- coding: utf-8 -*-

import os
import re
import sys
import urllib
import urllib2
import xbmcplugin
import xbmcgui
import xbmcaddon

import XbmcHelpers
common = XbmcHelpers

class FirstTV():
    def __init__(self):
        self.id = 'plugin.video.1tv.ru'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.xpath = sys.argv[0]
        self.handle = int(sys.argv[1])
        self.params = sys.argv[2]

        self.language = self.addon.getLocalizedString
        self.inext = os.path.join(self.path, 'resources/icons/next.png')

        self.url = 'http://www.1tv.ru'
        self.stream_url = 'http://stream.1tv.ru'
        self.archive_url = 'http://www.1tv.ru/projects/'
        self.video_stream_url = 'http://www.1tv.ru/owa/win/one_sp_common.promo_single_xml'

        self.playlist_url = 'http://stream.1tv.ru/nplaylist/1tvch.xml'
        self.live_stream_url = 'http://cdn9.1internet.tv/hls-live2/livepkgr/_definst_/'
        self.streams = {'1': '1tv/1tv1.m3u8', '2': '1tv/1tv2.m3u8', '3': '1tv/1tv3.m3u8'}

    def main(self):
        params = common.getParameters(self.params)
        mode = params['mode'] if 'mode' in params else None
        url = urllib.unquote(params['url']) if 'url' in params else None
        page = int(params['page']) if 'page' in params else 1
        project_id = params['project_id'] if 'project_id' in params else None
        video_id = params['video_id'] if 'video_id' in params else None

        if mode == 'play_stream':
            self.play_stream(url)
        if mode == 'play_video':
            self.play_video(project_id, video_id)
        if mode == 'live':
            self.live()
        if mode == 'project':
            self.project(project_id, page)
        if mode == 'projects':
            self.projects(page)
        elif mode is None:
            self.index()

    def index(self):
        uri = sys.argv[0] + '?mode=live'
        item = xbmcgui.ListItem('[B]%s[/B]' % self.language(1000), iconImage=self.icon, thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=projects'
        item = xbmcgui.ListItem('[B]%s[/B]' % self.language(1001), iconImage=self.icon, thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmcplugin.endOfDirectory(self.handle, True)

    def live(self):
        uri = sys.argv[0] + '?mode=play_stream&url=%s' % self.live_stream_url + self.streams['1']
        item = xbmcgui.ListItem('%s 1 [COLOR=55FFFFFF](SD)[/COLOR]' % self.language(1002), iconImage=self.icon, thumbnailImage=self.icon)
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        uri = sys.argv[0] + '?mode=play_stream&url=%s' % self.live_stream_url + self.streams['2']
        item = xbmcgui.ListItem('%s 2 [COLOR=55FFFFFF](SD)[/COLOR]' % self.language(1002), iconImage=self.icon, thumbnailImage=self.icon)
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        uri = sys.argv[0] + '?mode=play_stream&url=%s' % self.live_stream_url + self.streams['3']
        item = xbmcgui.ListItem('%s 3 [COLOR=55FFFFFF](HD)[/COLOR]' % self.language(1002), iconImage=self.icon, thumbnailImage=self.icon)
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        xbmcplugin.endOfDirectory(self.handle, True)

    def projects(self, page):
        print "Projects page: %d" % page
        url = 'http://www.1tv.ru/owa/win/ONE_PROJECTS.shed_project_list?p_pagenum=%s' % page

        response = common.fetchPage({'link': url})
        content = common.parseDOM(response['content'], 'div', attrs={'id': 'list_abc_search'})

        projects = common.parseDOM(content, 'h3')
        titles = common.parseDOM(projects, 'a')

        links_container = common.parseDOM(content, 'h5')
        links = common.parseDOM(links_container, 'a', ret='href')
        images = common.parseDOM(content, 'img', ret='src')

        infos_container = common.parseDOM(content, 'p')
        infos = common.parseDOM(infos_container, 'span')

        dates = common.parseDOM(content, 'div', attrs={'class': 'date'})
        genres = common.parseDOM(content, 'div', attrs={'class': 'tags'})

        for i, title in enumerate(titles):
            date  = self.encode(dates[i]).split(' ')
            title = "%s %s" % (self.encode(common.stripTags(str(title))), '[COLOR=55FFFFFF](%s)[/COLOR]' % (date[0] + ' ' + date[1]))
            genre = self.encode(genres[i])
            info = self.encode(common.stripTags(infos[i])).replace('  ', '')
            project_id = links[i].split('&')[0].split('/')[-1].replace('si=', '')

            uri = sys.argv[0] + '?mode=project&project_id=%s' % project_id
            item = xbmcgui.ListItem(title, iconImage=self.icon, thumbnailImage=images[i])
            item.setInfo(type='Video', infoLabels={'title': title, 'genre': genre, 'plot': info})
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=projects&page=%d' % (page+1)
        item = xbmcgui.ListItem(self.language(1005), iconImage=self.inext)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def project(self, project_id, page):
        url = "http://www.1tv.ru/owa/win/one_sp_editions.editions_list?p_pagenum=%d&sn_id=%s&w_id=&nxt=0" % (page, project_id)

        content = common.fetchPage({'link': url})['content']
        videos = common.parseDOM(content, 'li')

        link_container = common.parseDOM(videos, 'p')
        text_container = common.parseDOM(videos, 'h3')

        titles = common.parseDOM(text_container, 'a')
        links = common.parseDOM(link_container, 'a', ret='href')
        images = common.parseDOM(videos, 'img', ret='src')

        dates = common.parseDOM(videos, 'div', attrs={'class': 'date'})
        infos = common.parseDOM(videos, 'p')

        for i, title in enumerate(titles):
            title = self.encode(title)
            date  = self.encode(dates[i]).replace('\n', '').split(',')[0]
            info  = self.encode(common.stripTags(infos[i])).replace('  ', '')

            video_id = links[i].split('/')[-1]

            uri = sys.argv[0] + '?mode=play_video&project_id=%s&video_id=%s' % (project_id, video_id)
            item = xbmcgui.ListItem(title, iconImage=self.icon, thumbnailImage=images[i])
            item.setInfo(type='Video', infoLabels={'title': title, 'genre': date, 'plot': info, 'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0})
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        uri = sys.argv[0] + '?mode=project&project_id=%s&page=%d' % (project_id, page+1)
        item = xbmcgui.ListItem(self.language(1005), iconImage=self.inext)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def play_video(self, project_id, video_id):
        playlist_url = "%s?pid=0&sn_id=%s&ed_id=%s" %(self.video_stream_url, project_id, video_id)
        request = urllib2.Request(playlist_url, headers={"Host" : "www.1tv.ru"})
        content = urllib2.urlopen(request).read()
        links = common.parseDOM(content, 'media:content', ret='url')
        url = links[0] if links else None

        if url:
            item = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(self.handle, True, item)
        else:
            self.showErrorMessage(self.language(1004).encode('utf-8'))

    def play_stream(self, url):
        item = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(self.handle, True, item)

    # Python helpers
    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')

    def showErrorMessage(self, msg):
        header = self.language(1003).encode('utf-8')
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)"%(header, msg, str(5*1000)))

FirstTV().main()

