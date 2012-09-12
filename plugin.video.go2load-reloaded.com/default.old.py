#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *      Copyright (C) 2011 by Tolin
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

import urllib2, re, httplib, xbmc, xbmcaddon, xbmcgui, xbmcplugin, cookielib, xbmcaddon, os, urllib, urllib2, socket

Addon = xbmcaddon.Addon(id='plugin.go2load.com')
icon    = Addon.getAddonInfo('icon')

siteUrl = 'go2load.com'
httpSiteUrl = 'http://' + siteUrl

h = int(sys.argv[1])


def playItem(url):
    item = xbmcgui.ListItem(path = url)
    player = FlashPlayer()
    player.play(url, item)
        
    while(1):
        xbmc.sleep(500)

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
    
# MAIN()
params = get_params()

# TODO: code refactoring
url=None
mode=None
categorie=None
thumbnail=None
page=None

try:
    mode=params['mode'].upper()
except: pass
try:
    url=urllib.unquote_plus(params['url'])
except: pass
try:
    categorie=params['categorie']
except: pass
try:
    thumbnail=urllib.unquote_plus(params['thumbnail'])
except: pass
try:
    page=params['page']
except: pass

if mode == 'PLAY':
    playItem(url)
elif mode == None:
    url = BASE_URL if url == None else url
    getRecentItems(url)