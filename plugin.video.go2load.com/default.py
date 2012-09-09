#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.6
# -*- coding: utf-8 -*-

import urllib, re, os, sys
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import CommonFunctions

from helpers import * 

BASE_URL = 'http://go2load.com'

common = CommonFunctions
pluginhandle = int(sys.argv[1])

Addon = xbmcaddon.Addon(id='plugin.video.filin.tv')
addon_icon    = Addon.getAddonInfo('icon')
addon_path    = Addon.getAddonInfo('path')

# <li class="alt"><a href="/filmy/" style="font-size: 12px; padding-left: 10px;">FILMS</a></li>
# <li><a href="/video/mult/" style="font-size: 12px; padding-left: 10px;">MULTFILMS</a></li>
# <li class="alt"><a href="/documentary/" style="font-size: 12px; padding-left: 10px;">Documentary</a></li>
# <li class="alt"><a href="/filmy/cccp/" style="font-size: 12px; padding-left: 10px;">SSSR</a></li>
# <li><a href="/filmy/comedy_club_ukraine/">Comedy Club Ukraine</a></li>
# <li class="alt"><a href="/529-.html">Nasha Russia</a></li>
# <li><a href="/flash/flash_video/">Flash video</a></li>
# <li class="alt"><a href="/filmy/actors/">Actors</a></li>
# <li class="alt"><a href="/clips/">Clips</a></li>


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
    uri = sys.argv[0] + '?mode=CATEGORYITEMS' + '&url=' + url + '/clips/'
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

        #newspaneopen = common.parseDOM(http["content"], "div", attrs = { "class":"newspaneopen" })
        #header = common.parseDOM(newspaneopen, "h4")
        #titles = common.parseDOM(header, "a")
         
         #genres = common.parseDOM(newspaneopen, "td", attrs = { "align":"right" })
        

        print len(titles)
        print len(uniq(links))
        
        #print str(len(links))
#         for i, link in enumerate(uniq(links)):
#             print "#" + str(i) +  link
#         for i, title in enumerate(titles):
#             print "#" + str(i)+  unescape(title, 'cp1251')
#         for i, thumb in enumerate(uniq(thumbnails)):
#             print "#" + str(i) + thumb
                              
        print links     
        for i, link in enumerate(uniq(links)):
        #for i in range(0, len(titles)):
            try:
                title = unescape(titles[i], 'cp1251')
                thumbnail = thumbnails[i] if thumbnails[i].split(':')[0] == 'http' else BASE_URL + thumbnails[i]
            except IndexError:
                title = 'Empty'
                thumbnail = ''
            else:        
                item = xbmcgui.ListItem(title, thumbnailImage=thumbnail)
                uri = sys.argv[0] + '?mode=GETITEMS' + '&url=' + links[i]
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
            
            
        
        if len(uniq(links)) == 25:
            print url[-1]
            print url[:-1]
    
            
            next = url[:-1] + str(int(url[-1])+1)
            
            print next
            
            item = xbmcgui.ListItem('next page >>')
            uri = sys.argv[0] + '?mode=NEXTPAGE' + '&url=' + next
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True) 
            
    else:
        # TODO: add error message helper
        print "Show error message"
    
    
    xbmcplugin.endOfDirectory(pluginhandle, True)


def getPlayableItems(url):
    http = common.fetchPage({"link": url})
    
    if http["status"] == 200:
        content = common.parseDOM(http["content"], "div", attrs = { "class":"story_content" })
        links = common.parseDOM(content, "a", ret="href")
        links = list(set(links))
        
        counter = False

        for i,url in enumerate(uniq(links)):
            if url.split(':')[0] == 'ftp' and (url.find(".mkv") != -1 or url.find(".avi") != -1):
                found = True
                name = url.split('/')[-1]
                item = xbmcgui.ListItem(name)
                uri = sys.argv[0] + '?mode=PLAY' + '&url=' + url
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)                

        
        if found == False:
            #print "*** FTP not found, looking for flash player"
            
            embed = common.parseDOM(content, "embed", ret="videoUrl")
                
            if len(embed) != 0:
                url = embed[0].split('&amp;')[0]
                #print "*** Flash link found " + url
                
                name = url.split('/')[-1]
                item = xbmcgui.ListItem(name)
                uri = sys.argv[0] + '?mode=PLAY' + '&url=' + url
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
            else: 
                print "### Playable URL not found :("
                                


    else:
        # TODO: add error message helper
        print "Show error message"

    xbmcplugin.endOfDirectory(pluginhandle, True)

    
def playItem(url):
    item = xbmcgui.ListItem(path = url)
    player = xbmc.Player()
    player.play(url, item)

    
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