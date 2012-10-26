#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.0
# -*- coding: utf-8 -*-

import urllib, urllib2, socket
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import CommonFunctions
common = CommonFunctions


class Imtv():
    def __init__(self):
        self.id = 'plugin.video.imtv.at.ua'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])
        self.url = 'http://imtv.at.ua'

    def main(self):
        params = common.getParameters(sys.argv[2])
        mode = url = category = None

        mode = params['mode'] if params.has_key('mode') else None
        url = urllib.unquote_plus(params['url']) if params.has_key('url') else None
        category = params['category'] if params.has_key('category') else None

        if mode == 'play':
            self.play(url)
        if mode == 'channels':
            self.getChannels(category)
        elif mode == None:
            self.menu()

    def menu(self):
        self.getCategories()


    def getCategories(self):
        response = common.fetchPage({"link": self.url})

        if response["status"] == 200:
            select = common.parseDOM(response["content"], "select", attrs = { "id":"ch" })
            categories = common.parseDOM(select, "optgroup", ret="label")

            for i,category in enumerate(categories):
                uri = sys.argv[0] + '?mode=channels&category=%s'%i
                item = xbmcgui.ListItem(category, iconImage = self.icon, thumbnailImage = self.icon)
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
        else:
            showErrorMessage("*** ERROR in index(), bad response status%s"%response["status"])

        xbmcplugin.endOfDirectory(self.handle, True)


    def getChannels(self, category):
        print "*** Category %s"%category
        response = common.fetchPage({"link": self.url})

        if response["status"] == 200:
            select = common.parseDOM(response["content"], "select", attrs = { "id":"ch" })
            categories = common.parseDOM(select, "optgroup")
            channels = common.parseDOM(categories[int(category)], "option")
            links = common.parseDOM(categories[int(category)], "option", ret="value")

            for i,channel in enumerate(channels):
                uri = sys.argv[0] + '?mode=play&url=%s'%links[i]
                item = xbmcgui.ListItem(channel, iconImage = self.icon, thumbnailImage = self.icon)
                item.setInfo( type="Video", infoLabels={ "Title": channel } )
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
        else:
            showErrorMessage("*** ERROR in index(), bad response status%s"%response["status"])

        xbmcplugin.endOfDirectory(self.handle, True)

    def play(self, url):
      item = xbmcgui.ListItem(path = url)
      xbmcplugin.setResolvedUrl(self.handle, True, item)

    def showErrorMessage(text):
        print text

#    def addLink(name,url,iconimage):
#        ok=True
#        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
#        liz.setInfo( type="Video", infoLabels={ "Title": name } )
#        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
#        return ok


#    def addDir(name,url,mode,iconimage):
#        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
#        ok=True
#        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
#        liz.setInfo( type="Video", infoLabels={ "Title": name } )
#        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
#        return ok

imtv = Imtv()
imtv.main()
