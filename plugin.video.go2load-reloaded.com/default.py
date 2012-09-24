#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.0
# -*- coding: utf-8 -*-

import urllib, re, os, sys
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import CommonFunctions

from helpers import * 

BASE_URL = 'http://go2load.com'

common = CommonFunctions
pluginhandle = int(sys.argv[1])

Addon = xbmcaddon.Addon(id='plugin.video.go2load-reloaded.com')
addon_icon    = Addon.getAddonInfo('icon')
addon_path    = Addon.getAddonInfo('path')


def getCategories(url):
    item = xbmcgui.ListItem('Films')
    uri = sys.argv[0] + '?mode=CATEGORYITEMS' + '&url=' + url + '/filmy/page/1/'
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
    
    item = xbmcgui.ListItem('Multfilms')
    uri = sys.argv[0] + '?mode=CATEGORYITEMS' + '&url=' + url + '/filmy/mult/page/1/'
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    item = xbmcgui.ListItem('USSR films')
    uri = sys.argv[0] + '?mode=CATEGORYITEMS' + '&url=' + url + '/filmy/cccp/page/1/'
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        
    item = xbmcgui.ListItem('Documentary')
    uri = sys.argv[0] + '?mode=CATEGORYITEMS' + '&url=' + url + '/documentary/page/1/'
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    item = xbmcgui.ListItem('Clips')
    uri = sys.argv[0] + '?mode=CATEGORYITEMS' + '&url=' + url + '/clips/page/1/'
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    xbmcplugin.endOfDirectory(pluginhandle, True)

def getCategoryItems(url):
    http = common.fetchPage({"link": url})
    
    if http["status"] == 200:
        content = common.parseDOM(http["content"], "div", attrs = { "class":"story_content" })
        center = common.parseDOM(content, "div", attrs = { "align":"center" })
        
        links = common.parseDOM(content, "a", ret="href")
        thumbnails = common.parseDOM(content, "img", ret="src")
        titles = common.parseDOM(content, "img", ret="alt")

        for i, link in enumerate(uniq(links)):
        #for i in range(0, len(titles)):
            try:
                title = unescape(titles[i], 'cp1251')
                thumbnail = thumbnails[i] if thumbnails[i].split(':')[0] == 'http' else BASE_URL + thumbnails[i]
            except IndexError:
                title = 'Empty'
                thumbnail = addon_icon
                pass
            else:        
                item = xbmcgui.ListItem(title, thumbnailImage=thumbnail)
                uri = sys.argv[0] + '?mode=GETITEMS' + '&url=' + links[i]
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
            
            
        
    
            
        next = url[:-1] + str(int(url[-1])+1)
            
        print "*** Next page is " + next
            
        item = xbmcgui.ListItem('next page >>')
        uri = sys.argv[0] + '?mode=NEXTPAGE' + '&url=' + next
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True) 
            
    else:
        # TODO: add error message helper
        print "Show error message"
    
    
    xbmcplugin.endOfDirectory(pluginhandle, True)


def getPlayableItems(url):
    http = common.fetchPage({"link": url})
    found = False
    
    if http["status"] == 200:
        content = common.parseDOM(http["content"], "div", attrs = { "class":"story_content" })
        #left = common.parseDOM(content, "div", attrs = { "align":"left" })
        
        links = common.parseDOM(content, "a", ret="href")
        print links

#         links = list(set(links))
        
        for i,url in enumerate(uniq(links)):
            if url.split(':')[0] == 'ftp':
                print "*** This is a FTP link"
                if url.find(".mkv") != -1 or url.find(".avi") != -1 or url.find(".mp4") != -1:
                    found = True
                    name = url.split('/')[-1]
                    item = xbmcgui.ListItem(name)
                    uri = sys.argv[0] + '?mode=PLAY' + '&url=' + url
                    item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)
            elif url.split(':')[0] == 'http':
                print "*** This is a HTTP link" 
                if url.find(".mkv") != -1 or url.find(".avi") != -1 or url.find(".mp4") != -1:
                    found = True
                    name = url.split('/')[-1]
                    item = xbmcgui.ListItem(name)
                    uri = sys.argv[0] + '?mode=PLAY' + '&url=' + url
                    item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)
        
        if found == False:
            print "*** FTP not found, looking for flash player"
            url = common.parseDOM(content, "embed", ret="src")
            videoUrl = common.parseDOM(content, "embed", ret="videoUrl")
            mediaLink = common.parseDOM(content, "embed", ret="MediaLink")
                
            if videoUrl or mediaLink:
                url = videoUrl[0].split('&')[0] if videoUrl else mediaLink[0].split('&')[0]
                name = url.split('/')[-1]
                uri = sys.argv[0] + '?mode=PLAY' + '&url=' + url
                item = xbmcgui.ListItem(name)
                item.setProperty('IsPlayable', 'true')            
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)
            elif url:
                #if url.find(".mkv") != -1
                print url              

#                 name = url.split('/')[-1]
#                 uri = sys.argv[0] + '?mode=PLAY' + '&url=' + url
#                 item = xbmcgui.ListItem(name)
#                 item.setProperty('IsPlayable', 'true')            
#                 xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)
                 
            else: 
                print "### Playable URL not found :("
                                


    else:
        # TODO: add error message helper
        print "Show error message"

    xbmcplugin.endOfDirectory(pluginhandle, True)

    
def playItem(url):
    item = xbmcgui.ListItem(path = url)  
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

    
def main():
    url=None
    mode=None
    
    params = get_params()
    
    try:
        mode=params['mode'].upper()
    except: pass
    try:
        url=urllib.unquote_plus(params['url'])
    except: pass


    if mode == 'PLAY':
        playItem(url)
    if mode == 'NEXTPAGE':
        getCategoryItems(url)
    if mode == 'GETITEMS':
        getPlayableItems(url)
    elif mode == 'CATEGORYITEMS':
        getCategoryItems(url)
    elif mode == None:
        getCategories(BASE_URL)

main()