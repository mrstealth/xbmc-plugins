#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.4
# -*- coding: utf-8 -*-

import urllib, urllib2, re, os, sys, socket
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import CommonFunctions

BASE_URL = 'http://uakino.net'

common = CommonFunctions
pluginhandle = int(sys.argv[1])

Addon = xbmcaddon.Addon(id='plugin.video.uakino-reloaded.net')
addon_icon  = Addon.getAddonInfo('icon')
addon_path  = Addon.getAddonInfo('path')
addon_icons = os.path.join(addon_path, 'resources', 'icons')


lang  = Addon.getLocalizedString
handle = int(sys.argv[1])


def construct_uri(params):
  return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def uniq(a):
    if len(a) == 0:
        return []
    else:
        return [a[0]] + uniq([x for x in a if x != a[0]])

def home():
    item = xbmcgui.ListItem(lang(3005))
    uri = sys.argv[0] + '?mode=SUBCATEGORY&path=category/video/900' + '&category=' + lang(3005)
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    item = xbmcgui.ListItem(lang(3004))
    uri = sys.argv[0] + '?mode=SUBCATEGORY&path=category/video/137' + '&category=' + lang(3004)
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    item = xbmcgui.ListItem(lang(3000))
    uri = sys.argv[0] + '?mode=CATEGORY&path=category/video/59' + '&category=' + lang(3000)
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    item = xbmcgui.ListItem(lang(3001))
    uri = sys.argv[0] + '?mode=CATEGORY&path=category/video/64' + '&category=' + lang(3001)
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    item = xbmcgui.ListItem(lang(3002))
    uri = sys.argv[0] + '?mode=CATEGORY&path=category/video/65' + '&category=' + lang(3002)
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    item = xbmcgui.ListItem(lang(3003))
    uri = sys.argv[0] + '?mode=CATEGORY&path=category/video/68' + '&category=' + lang(3003)
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    item = xbmcgui.ListItem(lang(2002))
    uri = sys.argv[0] + '?mode=CATALOG&path=videoclip' + '&category=' + lang(2002)
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    xbmcplugin.endOfDirectory(pluginhandle, True)


def getCatalogs(url, category, path):
    print "*** getCatalogs %s"%category
    print "*** getCatalogs %s"%path

    if path == '/':
        getSubCategories(BASE_URL,'',0,category)
    elif path == 'video':
        item = xbmcgui.ListItem(lang(3000))
        uri = sys.argv[0] + '?mode=CATEGORY&path=category/video/59' + '&category=' + lang(3000)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

        item = xbmcgui.ListItem(lang(3001))
        uri = sys.argv[0] + '?mode=CATEGORY&path=category/video/64' + '&category=' + lang(3001)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

        item = xbmcgui.ListItem(lang(3002))
        uri = sys.argv[0] + '?mode=CATEGORY&path=category/video/65' + '&category=' + lang(3002)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

        item = xbmcgui.ListItem(lang(3003))
        uri = sys.argv[0] + '?mode=CATEGORY&path=category/video/68' + '&category=' + lang(3003)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
    elif path == 'videoclip':
        item = xbmcgui.ListItem(lang(4000))
        uri = sys.argv[0] + '?mode=CATEGORY&path=category/videoclip/141' + '&category=' + lang(4000)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

        item = xbmcgui.ListItem(lang(4001))
        uri = sys.argv[0] + '?mode=CATEGORY&path=category/videoclip/150' + '&category=' + lang(4001)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

        item = xbmcgui.ListItem(lang(4002))
        uri = sys.argv[0] + '?mode=CATEGORY&path=category/videoclip/158' + '&category=' + lang(4002)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)


    xbmcplugin.endOfDirectory(pluginhandle, True)

# get links for given category
def getCategories(url, category):
    print "### getCategories:%s"%category
    print url

    page = common.fetchPage({"link": url})
    media_line = common.parseDOM(page["content"], "div", attrs = { "class":"tab media_line" })
    about = common.parseDOM(media_line, "div", attrs = { "class":"about" })
    titles = common.parseDOM(media_line, "a", ret="title")
    paths = uniq(common.parseDOM(media_line, "a", ret="href"))

    for i, title in enumerate(titles):
        item = xbmcgui.ListItem(title)
        uri = sys.argv[0] + '?mode=SUBCATEGORY&path=%s'%paths[i] + '&category=' + category
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    xbmcplugin.endOfDirectory(pluginhandle, True)


def getSubCategories(url,path,offset,category):
    print "### getSubCategories:%s"%category
    print url

    page = common.fetchPage({"link": url})
    media_line = common.parseDOM(page["content"], "div", attrs = { "class":"tab media_line" })

    titlesA = common.parseDOM(media_line, "a", ret="title")
    pathsA = common.parseDOM(media_line, "a", attrs = {"class":"fleft thumb"}, ret="href")

    titlesB = common.parseDOM(media_line, "a", attrs = {"class":"heading"})
    pathsB = common.parseDOM(media_line, "a", attrs = {"class":"heading"}, ret="href")

    thumbs = common.parseDOM(media_line, "img", ret="src")

    offset = 16 if offset == None else (int(offset)+16)

    if titlesA and titlesB:
        next = False if len(titlesA) + len(titlesB) < 16 else True
        print "*** this is a mix of both"
        for i, title in enumerate(titlesA):
            thumb = BASE_URL + thumbs[i] if thumbs[i].find("http") == -1 else thumbs[i]
            item = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage = thumb)
            uri = sys.argv[0] + '?mode=SUBCATEGORY&path=%s'%pathsA[i] + '&category=' + category
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

        for i, title in enumerate(titlesB):
            thumb = BASE_URL + thumbs[len(titlesA)+i] if not thumbs[i].find("http") == -1 else thumbs[len(titlesA)+i]
            item = xbmcgui.ListItem(title, iconImage = thumb, thumbnailImage = thumb)
            uri = sys.argv[0] + '?mode=ITEMS&path=%s'%pathsB[i] + '&category=' + category
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    elif titlesA:
        next = False if len(titlesA) < 16 else True

        print "*** this is a list of season with multiple items?"

        if url == 'http://uakino.net/category/video/52':
            print "*** this is a list of links " + category
            getCategories(url, category)
        else:
            for i, title in enumerate(titlesA):
                thumb = BASE_URL + thumbs[i] if thumbs[i].find("http") == -1 else thumbs[i]
                item = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage = thumb)
                uri = sys.argv[0] + '?mode=SUBCATEGORY&path=%s'%pathsA[i] + '&category=' + category
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    elif titlesB:
        print "*** this is a list of videos with one playable item?"
        next = False if len(titlesB) < 16 else True

        ul = common.parseDOM(media_line, "ul")

        for i, title in enumerate(titlesB):
            thumb = BASE_URL + thumbs[i] if thumbs[i].find("http") == -1 else thumbs[i]
            genres = common.stripTags(common.parseDOM(ul[i], "li")[0])

            try:
                description = common.stripTags(common.parseDOM(ul[i], "li")[2])
            except IndexError:
                description = common.stripTags(common.parseDOM(ul[i], "li")[1])

            item = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage = thumb)
            info = {'title': title, 'genre': genres, 'plot': description}
            item.setInfo( type='Video', infoLabels=info)

            uri = sys.argv[0] + '?mode=ITEMS&path=%s'%pathsB[i] + '&category=%s'%category
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)
    else:
      next = False

    if next:
        item = xbmcgui.ListItem('NEXT PAGE >>')
        uri = sys.argv[0] + '?mode=SUBCATEGORY&path=%s' + url
        uri += '&path=%s'%path
        uri += '&offset=%s'%str(offset)
        uri += '&category=' + category
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    xbmc.executebuiltin('Container.SetViewMode(52)')
    xbmcplugin.endOfDirectory(pluginhandle, True)


def getPlayableItems(url,category):
    print "### getPlayableItems:%s"%category
    page = common.fetchPage({"link": url})
    path = common.parseDOM(page["content"], "a", attrs = { "id":"player" }, ret="href")[0]
    play(construct_url(path))

def play(url):
    print "### play:%s"%url
    item = xbmcgui.ListItem(path = url)
    xbmcplugin.setResolvedUrl(handle, True, item)


def construct_url(path):
    print path
    return BASE_URL + '/' + path


def main():
    mode=None
    url=None
    path=None
    category=None
    offset=None

    params = common.getParameters(sys.argv[2])

    try:
        mode=params['mode'].upper()
    except: pass
    try:
        url=urllib.unquote_plus(params['url'])
    except: pass
    try:
        path=params['path']
    except: pass
    try:
        category=params['category']
    except: pass
    try:
        offset= params['offset']
    except: pass

    if mode == 'PLAY':
        playItem(url,title)
    if mode == 'ITEMS':
        getPlayableItems(construct_url(path), category)
    elif mode == 'SUBCATEGORY':
        if offset != None and int(offset) > 0:
            print offset
            url = construct_url(path) + '?order=date&offset=' + offset
        else:
            url = construct_url(path)

        getSubCategories(url, path, offset, category)
    elif mode == 'CATEGORY':
        getCategories(construct_url(path), category)
    elif mode == 'CATALOG':
        getCatalogs(construct_url(path), category, path)

    elif mode == None:
        home()

main()
