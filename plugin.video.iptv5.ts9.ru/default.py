#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.1
# -*- coding: utf-8 -*-

import xbmcplugin,xbmcgui,xbmcaddon
import os, urllib, CommonFunctions
import simplejson as json
import HTMLParser
from traceback import print_exc

common = CommonFunctions

pluginhandle = int(sys.argv[1])

Addon = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')
addon_icon    = Addon.getAddonInfo('icon')
addon_path    = Addon.getAddonInfo('path')

BASE_URL   = 'http://www.iptv5.ts9.ru/play.htm'

        
def unescape(entity, encoding):
  if encoding == 'utf-8':
    return HTMLParser.HTMLParser().unescape(entity).encode(encoding)
  elif encoding == 'cp1251':
    return entity.decode(encoding).encode('utf-8')

def xbmcItem(url, title, mode, *args):
    item = xbmcgui.ListItem(title)
    uri = sys.argv[0] + '?mode='+ mode + '&url=' + url
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

def xbmcContextMenuItem(item, action, label, url, title):
    script = "special://home/addons/plugin.video.iptv5.ts9.ru/contextmenu.py"
    params = action + "|%s"%url + "|%s"%title
    runner = "XBMC.RunScript(" + str(script)+ ", " + params + ")"
    item.addContextMenuItems([(label, runner)])
       
def listFavorites():
    string = Addon.getSetting('favorites')
    label = unescape("&#1059;&#1076;&#1072;&#1083;&#1080;&#1090;&#1100; &#1080;&#1079; &#1089;&#1087;&#1080;&#1089;&#1082;&#1072; &#1092;&#1072;&#1074;&#1086;&#1088;&#1080;&#1090;&#1086;&#1074;", 'utf-8')
    
    if len(string) == 0:
        item = xbmcgui.ListItem()
        item.setProperty('IsPlayable', 'false')
        xbmcplugin.addDirectoryItem(pluginhandle, '', item, True)
    else:
        favorites = json.loads(string)
        
        for key in favorites:
            print "Found favorite " + key
            item = xbmcgui.ListItem(favorites[key])
            uri = sys.argv[0] + '?mode=PLAY2'
            uri += '&url=' + urllib.quote_plus(key)
            uri += '&title=' + favorites[key]
            
            item.setInfo( type='Video', infoLabels={'title': favorites[key]})
            item.setProperty('IsPlayable', 'true')

            xbmcContextMenuItem(item, 'remove', label, key, favorites[key])
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
       
    xbmcplugin.endOfDirectory(pluginhandle, True)
    
def get_groups(url):
    page = common.fetchPage({"link": url})
    
    fav = unescape("&#1060;&#1072;&#1074;&#1086;&#1088;&#1080;&#1090;&#1099;", "utf-8")
    xbmcItem('', "[COLOR FF00FFF0][" + fav + "][/COLOR]", 'FAVORITES')

    if page["status"] == 200:       
        select = common.parseDOM(page["content"], "select", attrs = { "id":"ch" }) 
        optgroups = common.parseDOM(select, "optgroup", ret="label")[0:-1]
        options = common.parseDOM(select, "optgroup")
        
        for i in range(len(optgroups)):
            channels = {}
            
            titles = common.parseDOM(options[optgroups.index(optgroups[i])], "option")
            links = common.parseDOM(options[optgroups.index(optgroups[i])], "option", ret="value")
            
            for x, title in enumerate(titles):
                channels[links[x]] = unescape(titles[x], 'cp1251')
            
            group = unescape(optgroups[i], 'cp1251')
            Addon.setSetting(group, json.dumps(channels))
                            
            uri = sys.argv[0] + '?mode=SHOW'
            uri += '&url=' + urllib.quote_plus(BASE_URL)
            uri += '&group=' + group
            
            item = xbmcgui.ListItem(optgroups[i], iconImage=addon_icon, thumbnailImage=addon_icon)
            item.setInfo( type='video', infoLabels={'title': optgroups[i]})            
            
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
    
    xbmc.executebuiltin('Container.SetSortMethod(9)')
    xbmcplugin.endOfDirectory(pluginhandle, True) 
    
def get_channels(url, group):
    label = unescape("&#1044;&#1086;&#1073;&#1072;&#1074;&#1080;&#1090;&#1100; &#1074; '&#1052;&#1086;&#1080; &#1060;&#1072;&#1074;&#1086;&#1088;&#1080;&#1090;&#1099;'", 'utf-8')
    page = common.fetchPage({"link": url})

    if page["status"] == 200:       
        select = common.parseDOM(page["content"], "select", attrs = { "id":"ch" }) 
        optgroups = common.parseDOM(select, "optgroup", ret="label")
        options = common.parseDOM(select, "optgroup")
                    
        channels = json.loads(Addon.getSetting(group))
        
        for url,title in channels.iteritems():
            name = unescape(title, 'utf-8')
            uri = sys.argv[0] + '?mode=PLAY'
            uri += '&url=' + urllib.quote_plus(url)
            uri += '&title=' + name
            
            item = xbmcgui.ListItem(name, iconImage=addon_icon, thumbnailImage=addon_icon)
            item.setInfo( type='video', infoLabels={'title': name})
            item.setProperty('IsPlayable', 'true')
            
            xbmcContextMenuItem(item, 'add', label, url, title)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item)
    
    xbmc.executebuiltin('Container.SetSortMethod(9)')
    xbmcplugin.endOfDirectory(pluginhandle, True)
    

def play_fav(url):
    xbmc.Player().play(url)
         
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
    get_channels(BASE_URL, group)
elif mode == 'FAVORITES':
    listFavorites();
elif mode == None: 
    get_groups(BASE_URL)
