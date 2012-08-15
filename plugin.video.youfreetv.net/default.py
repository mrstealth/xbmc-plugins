# -*- coding: utf-8 -*-
#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.0

import re
import urllib,urllib2,re,sys,os,time
import xbmcplugin,xbmcgui,xbmcaddon
import CommonFunctions

common = CommonFunctions
common.plugin = "Youfreetv.net"
common.dbg = False # Default (True)
common.dbglevel = 3 # Default

pluginhandle = int(sys.argv[1])
__addon__    = xbmcaddon.Addon(id='plugin.video.youfreetv.net') 

URL         = 'http://www.youfreetv.net'
CHANNEL_URL = 'http://www.youfreetv.net/index.php?section=channel'

# TODO: move to helper functions
# def unescape(s):
#     s = s.replace("%20", " ")
#     s = s.replace("%3C", "<")
#     s = s.replace("%3E", ">")
#     s = s.replace("%23", "#")
#     s = s.replace("%25", "%")
#     s = s.replace("%7B", "{")
#     s = s.replace("%7D", "}")
#     s = s.replace("%7C", "|")
#     s = s.replace("%5E", "^")
#     s = s.replace("%7E", "")
#     s = s.replace("%5B", "[")
#     s = s.replace("%5E", "]")
#     s = s.replace("%60", "‘")
#     s = s.replace("%3B", ";")
#     s = s.replace("%2F", "/")
#     s = s.replace("%3F", "?")
#     s = s.replace("%3A", ":")
#     s = s.replace("%40", "@")
#     s = s.replace("%3D", "=")
#     s = s.replace("%26", "&")
#     s = s.replace("%24", "$")
# 
#     return s
    
def get_channels(url):
    result = common.fetchPage({"link": url})

    if result["status"] == 200:
        ul = common.parseDOM(result["content"], "ul", attrs = { "id":"channels" })   
        links = common.parseDOM(ul, "a", ret = "href")
        values = common.parseDOM(ul, "a", ret ="value")
        thumbnails = common.parseDOM(ul, "img", ret ="src")       
        
        if len(links):
            for i,href in enumerate(links):
                if href != '#':
                    channel = values[i].replace('"', '').split('&')[0].upper()
                    uri = sys.argv[0] + '?mode=PLAY&channel=%s'%channel
                    uri += '&url='+urllib.quote_plus(href)
                    
                    item = xbmcgui.ListItem(channel, iconImage="icon.png", thumbnailImage=URL+thumbnails[i][1:])
                    item.setInfo( type='video', infoLabels={'title': channel, 'plot': 'Description'})
                    item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(pluginhandle, uri, item)

    xbmcplugin.endOfDirectory(pluginhandle, True, True, True)     
     
def play_url(url,channel):
    furl  = 'rtmp://50.7.168.98:1935/live/%s'%(channel + '.stream')
    furl += ' swfUrl=http://www.youfreetv.net/medien/player.php?file=swf swfvfy=true '
    furl += ' pageUrl=http://www.youfreetv.net/index.php?section=channel&amp;value=' + channel + '&amp;hd=false'
    furl += ' tcUrl=http://megaserver.youfreetv.net:1935/live'
    furl += ' flashVer=\'WIN 11,2,202,235\''
    
    item = xbmcgui.ListItem(channel, iconImage="icon.png", thumbnailImage="icon.png", path=furl)
    item = xbmcgui.ListItem(path = furl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
             
# TODO: code refactoring
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

# TODO: code refactoring
url=None
mode=None
channel=None

try:
    mode=params['mode']
except: pass

try:
    url=urllib.unquote_plus(params['url'])
except: pass

if mode == 'PLAY':
    channel=params['channel']
    play_url(url, channel.lower())
elif mode == None: get_channels(CHANNEL_URL)


