#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.1
# -*- coding: utf-8 -*-

import xbmcplugin,xbmcgui,xbmcaddon
import os, sys, urllib, urllib2
import HTMLParser, CommonFunctions
import socket, datetime
import simplejson as json
common = CommonFunctions

pluginhandle = int(sys.argv[1])

Addon = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')
addon_icon    = Addon.getAddonInfo('icon')
addon_path    = Addon.getAddonInfo('path')

BASE_URL   = 'http://www.iptv5.ts9.ru/play.htm'

today = datetime.date.today()
# save last check for each URL
def check_url(url):
#    today = datetime.date.today()
#    yesterday = today - datetime.timedelta(days=1)

    #last_check = Addon.getSetting('last-check')
    last_check = []
    if not last_check and last_check != str(today):
        if not url.find("rtsp") == -1: # skip rtsp check
            print "*** Skip rtsp check for " + url
            return True
        try:
            response = urllib2.urlopen(url, None, 1)
        except urllib2.HTTPError, e:
            print "***** Oops, HTTPError ", str(e.code)
            return False
        except urllib2.URLError, e:
            print "***** Oops, URLError", str(e.args)
            return False
        except socket.timeout, e:
            print "***** Oops timed out! ", str(e.args)
            return False
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return False
        else:
            return True
    else:
        print "*** Skip check for today, last check " + last_check
        return True


def unescape(entity, encoding):
  if encoding == 'utf-8':
    return HTMLParser.HTMLParser().unescape(entity).encode(encoding)
  elif encoding == 'cp1251':
    return entity.decode(encoding).encode('utf-8')

def xbmcItem(url, title, mode, *args):
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


def get_groups(url):
    # TODO: Improv category loading speed, load categories from settings if settings !!!
    # TODO NEXT: use sqlite.db as a storage instead of settings.xml

    page = common.fetchPage({"link": url})

    fav = unescape("&#1060;&#1072;&#1074;&#1086;&#1088;&#1080;&#1090;&#1099;", "utf-8")
    xbmcItem('', "[COLOR FF00FFF0][" + fav + "][/COLOR]", 'FAVORITES')

    if page["status"] == 200:
        select = common.parseDOM(page["content"], "select", attrs = { "id":"ch" })
        optgroups = common.parseDOM(select, "optgroup", ret="label")[0:-1]
        options = common.parseDOM(select, "optgroup")

        for i in range(len(optgroups)):
            group = {}
            channels = {}

            optgroup = optgroups[i]
            option = options[optgroups.index(optgroup)]
            groupname = unescape(optgroup, 'cp1251')

            titles = common.parseDOM(option, "option")
            links = common.parseDOM(option, "option", ret="value")

            for x, title in enumerate(titles):
                channels[links[x]] = unescape(titles[x], 'cp1251')

            if len(Addon.getSetting(groupname)) == 0 or ("checked_at" in group and group["checked_at"] != str(today)):
              group["channels"] = channels
              group["checked_at"] = ""
              Addon.setSetting(groupname, json.dumps(group))

            uri = sys.argv[0] + '?mode=SHOW'
            uri += '&url=' + urllib.quote_plus(BASE_URL)
            uri += '&group=' + groupname

            item = xbmcgui.ListItem(groupname, iconImage=addon_icon, thumbnailImage=addon_icon)
            item.setInfo( type='video', infoLabels={'title': groupname})

            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    xbmcplugin.endOfDirectory(pluginhandle, True)

def get_channels(url, groupname):
    label = unescape("&#1044;&#1086;&#1073;&#1072;&#1074;&#1080;&#1090;&#1100; &#1074; '&#1052;&#1086;&#1080; &#1060;&#1072;&#1074;&#1086;&#1088;&#1080;&#1090;&#1099;'", 'utf-8')

    group = json.loads(Addon.getSetting(groupname))
    channels = {}

    if url and group:
        for url,title in group["channels"].iteritems():
            name = unescape(title, 'utf-8')

            uri = sys.argv[0] + '?mode=PLAY'
            uri += '&url=' + urllib.quote_plus(url)

            if "checked_at" in group and len(group["checked_at"]) !=0 and group["checked_at"] == str(today):
                print "*** Everything is fine go ahead date of the last check is " + group['checked_at']

                item = xbmcgui.ListItem(name, iconImage=addon_icon, thumbnailImage=addon_icon)
                item.setInfo( type='video', infoLabels={'title': name})
                item.setProperty('IsPlayable', 'true')

                xbmcContextMenuItem(item, 'add', label, url, title)
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item)
            else:
                if check_url(url):
                    channels[url] = name
                    item = xbmcgui.ListItem(name, iconImage=addon_icon, thumbnailImage=addon_icon)
                    item.setInfo( type='video', infoLabels={'title': name})
                    item.setProperty('IsPlayable', 'true')

                    xbmcContextMenuItem(item, 'add', label, url, title)
                    xbmcplugin.addDirectoryItem(pluginhandle, uri, item)

    # save check results
    if channels:
      group["checked_at"] = str(today)
      group["channels"] = channels
      Addon.setSetting(groupname, json.dumps(group))

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
    get_channels(BASE_URL, group)
elif mode == 'FAVORITES':
    listFavorites();
elif mode == None:
    get_groups(BASE_URL)
