#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.5
# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-


import xbmcplugin,xbmcgui,xbmcaddon
import sys, urllib
import HTMLParser, CommonFunctions
import socket
import simplejson as json
common = CommonFunctions

pluginhandle = int(sys.argv[1])

Addon = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')
addon_icon    = Addon.getAddonInfo('icon')
addon_path    = Addon.getAddonInfo('path')
__settings__ = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')

BASE_URL   = 'http://www.iptv5.ts9.ru/play.htm'

from category import Category
category_db = Category('category.db')


def unescape(entity, encoding):
    if encoding == 'utf-8':
        return HTMLParser.HTMLParser().unescape(entity).encode(encoding)
    elif encoding == 'cp1251':
        return entity.decode(encoding).encode('utf-8')

def xbmcItem(mode, url, title):
    uri = sys.argv[0] + '?mode='+ mode + '&url=' + url
    item = xbmcgui.ListItem(title, iconImage=addon_icon, thumbnailImage=addon_icon)
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

def xbmcContextMenuItem(item, action, label, url, title):
    script = "special://home/addons/plugin.video.iptv5.ts9.ru/contextmenu.py"
    params = action + "|%s"%url + "|%s"%title
    runner = "XBMC.RunScript(" + str(script)+ ", " + params + ")"
    item.addContextMenuItems([(label, runner)])

def listFavorites():
    label = unescape("&#1059;&#1076;&#1072;&#1083;&#1080;&#1090;&#1100; &#1080;&#1079; &#1089;&#1087;&#1080;&#1089;&#1082;&#1072; &#1092;&#1072;&#1074;&#1086;&#1088;&#1080;&#1090;&#1086;&#1074;", 'utf-8')


    string = Addon.getSetting('favorites')
    if len(string) > 0:
      favorites = json.loads(string)

      for key in favorites:
          print "Found favorite " + key
          uri = sys.argv[0] + '?mode=PLAY2'
          uri += '&url=' + urllib.quote_plus(key)

          item = xbmcgui.ListItem(favorites[key], iconImage=addon_icon, thumbnailImage=addon_icon)
          item.setInfo( type='Video', infoLabels={'title': favorites[key]})
          item.setProperty('IsPlayable', 'true')

          xbmcContextMenuItem(item, 'remove', label, key, favorites[key])
          xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    xbmcplugin.endOfDirectory(pluginhandle, True)


def get_categories_from_url(url):
    print "*** get category from URL"
    page = common.fetchPage({"link": url})

    if page["status"] == 200:
        select = common.parseDOM(page["content"], "select", attrs = { "id":"ch" })
        optgroups = common.parseDOM(select, "optgroup", ret="label")[0:-1]
        options = common.parseDOM(select, "optgroup")

        categories = []

        for i in range(len(optgroups)):
            category = {}
            channels = {}

            optgroup = optgroups[i]
            option = options[optgroups.index(optgroup)]
            name = optgroup.decode('cp1251').encode('utf-8')

            # collect category name
            categories.append(name)

            titles = common.parseDOM(option, "option")
            links = common.parseDOM(option, "option", ret="value")

            for x, title in enumerate(titles):
                channels[links[x]] = title.decode('cp1251').encode('utf-8')

            # construct hash and save in DB
            category_db.add(name, json.dumps(channels))
    else:
        print "TODO: raise exception and show error dialog"

    return categories

def get_categories_from_db(url):
    print "*** get category from DB"
    fav = unescape("&#1060;&#1072;&#1074;&#1086;&#1088;&#1080;&#1090;&#1099;", "utf-8")
    xbmcItem('FAVORITES', '', "[COLOR FF00FFF0][" + fav + "][/COLOR]")

    # Hotfix
    entries = category_db.all()
    #entries = []

    # update categories once a day
    if len(entries) > 0:
        print "*** show categories"
        categories = entries
    else:
        print "*** get page and parse categories"
        categories = get_categories_from_url(url)

    for i, category in enumerate(categories):
        if not i == (len(categories)-1):
            uri = sys.argv[0] + '?mode=SHOW'
            uri += '&url=' + urllib.quote_plus(BASE_URL)
            uri += '&group=' + category

            item = xbmcgui.ListItem(category, iconImage=addon_icon, thumbnailImage=addon_icon)
            item.setInfo( type='video', infoLabels={'title': category})

            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        else:
            print bool(__settings__.getSetting('parent_control'))
            if not __settings__.getSetting('parent_control') == 'true':
                uri = sys.argv[0] + '?mode=SHOW'
                uri += '&url=' + urllib.quote_plus(BASE_URL)
                uri += '&group=' + category

                item = xbmcgui.ListItem(category, iconImage=addon_icon, thumbnailImage=addon_icon)
                item.setInfo( type='video', infoLabels={'title': category})

                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    xbmcplugin.endOfDirectory(pluginhandle, True)

def get_channels_from_url(category):
    print "*** get channels from URL"
    page = common.fetchPage({"link": BASE_URL})

    if page["status"] == 200:
        select = common.parseDOM(page["content"], "select", attrs = { "id":"ch" })
        optgroups = common.parseDOM(select, "optgroup", ret="label")[0:-1]
        options = common.parseDOM(select, "optgroup")

        translated = []
        for i in range(len(optgroups)):
            channels = {}

            name = optgroups[i].decode('cp1251').encode('utf-8')
            translated.append(name)
        print translated

            # optgroup = optgroups[i]
#             option = options[optgroups.index(optgroup)]
#             name = optgroup.decode('cp1251').encode('utf-8')
#
#             if category == name:
#                 print "***** CATEGORY FOUND"
#
#             titles = common.parseDOM(option, "option")
#             links = common.parseDOM(option, "option", ret="value")
#
#             for x, title in enumerate(titles):
#                 channels[links[x]] = title.decode('cp1251').encode('utf-8')
#
#             # construct hash and save in DB
#             #category_db.add(name, json.dumps(channels))
#             return channels
#     else:
#         print "TODO: raise exception and show error dialog"

    return []

def get_channels_from_db(name):
    print "*** get channels from DB"
    category = category_db.get(name)
    channels = json.loads(category['channels'])

    label = unescape('&#1044;&#1086;&#1073;&#1072;&#1074;&#1080;&#1090;&#1100; &#1074; "&#1060;&#1072;&#1074;&#1086;&#1088;&#1080;&#1090;&#1099;"', 'utf-8')

    for url in channels:
        title = channels[url].encode('utf-8')
        uri = sys.argv[0] + '?mode=PLAY' + '&url=' + urllib.quote_plus(url)

        item = xbmcgui.ListItem(title, iconImage=addon_icon, thumbnailImage=addon_icon)
        item.setInfo( type='video', infoLabels={'title': title})
        item.setProperty('IsPlayable', 'true')

        xbmcContextMenuItem(item, 'add', label, url, channels[url])
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item)

    xbmcplugin.endOfDirectory(pluginhandle, True)


def play_fav(url):
    item = xbmcgui.ListItem(path = url)
    xbmc.Player().play(url, item)


def play_url(url):
    item = xbmcgui.ListItem(path = url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param

params = get_params()

url=None
mode=None
group=None

try:
    mode=params['mode']
except: pass
try:
    url=urllib.unquote_plus(params['url'])
except: pass
try:
    group=params['group']
except: pass


if mode == 'PLAY':
    play_url(url)
elif mode == 'PLAY2':
    play_fav(url)
elif mode == 'SHOW':
    get_channels_from_db(group)
elif mode == 'FAVORITES':
    listFavorites();
elif mode == None:
    get_categories_from_db(BASE_URL)
