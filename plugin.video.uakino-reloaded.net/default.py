#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.0
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

lang  = Addon.getLocalizedString
handle = int(sys.argv[1])


def construct_uri(params):
  return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

#def showMessage(heading, message, times = 30000):
#    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, addon_icon))

def construct_url(path):
  return BASE_URL + path

def home():
    item = xbmcgui.ListItem(lang(2000))
    uri = sys.argv[0] + '?mode=CATALOG&path=/' + '&category=' + lang(2000)
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    item = xbmcgui.ListItem(lang(2001))
    uri = sys.argv[0] + '?mode=CATALOG&path=/video' + '&category=' + lang(2001)
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    item = xbmcgui.ListItem(lang(2002))
    uri = sys.argv[0] + '?mode=CATALOG&path=/videoclip' + '&category=' + lang(2002)
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    item = xbmcgui.ListItem(lang(2003))
    uri = sys.argv[0] + '?mode=CATALOG&path=/audio' + '&category=' + lang(2003)
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    xbmcplugin.endOfDirectory(pluginhandle, True)


def getCatalogs(url, category):
    print "### getCatalogs:%s"%category
    print url

    page = common.fetchPage({"link":url})
    catalog = common.parseDOM(page["content"], "li", attrs = { "class":"parent_closed" })
    categoris = common.parseDOM(catalog, "a")
    for i, title in enumerate(categoris):
        print title

    xbmcplugin.endOfDirectory(pluginhandle, True)

def getCategories(url, category):
    print "### getCategories:%s"%category
    xbmcplugin.endOfDirectory(pluginhandle, True)

def getSubCategories(url,category):
    print "### getSubCategories:%s"%category
    xbmcplugin.endOfDirectory(pluginhandle, True)


def getPlayableItems(url):
    http = common.fetchPage({"link": url})
    xbmcplugin.endOfDirectory(pluginhandle, True)


def playItem(url):
    item = xbmcgui.ListItem(path = url)
    player = xbmc.Player()
    player.play(url, item)


def main():
    mode=None
    url=None
    path=None
    category=None

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

    if mode == 'PLAY':
        playItem(url)
    if mode == 'NEXTPAGE':
        getCategoryItems(url)
    if mode == 'GETITEMS':
        getPlayableItems(url)
    elif mode == 'SUBCATEGORY':
        print path
        getSubCategories(construct_url(path), category)
    elif mode == 'CATEGORY':
        getCategories(construct_url(path), category)
    elif mode == 'CATALOG':
        getCatalogs(construct_url(path), category)

    elif mode == None:
        home()

main()
