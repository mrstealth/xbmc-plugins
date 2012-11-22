#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 2.0.2
# -*- coding: utf-8 -*-

import urllib, urllib2, httplib
import os, sys, socket, cookielib, errno
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import CommonFunctions
common = CommonFunctions


class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)
        result.status = code
        return result

    def http_error_302(self, req, fp, code, msg, headers):
        print "Authenticate and get real stream URL"
        return headers['Location']

class IPTV():
    def __init__(self):
        self.id = 'plugin.video.iptv5.ts9.ru'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')

        self.url = 'http://iptv5.ts9.ru/play.htm'
        self.handle = int(sys.argv[1])
        self.language = self.addon.getLocalizedString

    def main(self):
        params = common.getParameters(sys.argv[2])
        mode = url = category = None

        mode = params['mode'] if params.has_key('mode') else None
        url = urllib.unquote_plus(params['url']) if params.has_key('url') else None
        category = params['category'] if params.has_key('category') else None
        index = params['index'] if params.has_key('index') else None

        if mode == 'play':
            self.play(url)
        elif mode == 'channel':
            self.listChannels(url, index)
        elif mode == 'category':
            self.listCategories(url)
        elif mode == None:
            self.menu()


    def menu(self):
      self.listCategories(self.url)

      if self.addon.getSetting('parent_control') == 'false':
        uri = sys.argv[0] + '?mode=channel&url=http://iptv5.ts9.ru/playtv_18.htm&index=0'
        item = xbmcgui.ListItem(self.language(1001), iconImage = self.icon, thumbnailImage = self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

      xbmcplugin.endOfDirectory(self.handle, True)

    def listCategories(self, url):
        print "*** listCategories"

        response = common.fetchPage({"link": url})

        if response["status"] == 200:
            select = common.parseDOM(response["content"], "select", attrs = { "id":"ch" })
            groups = common.parseDOM(response["content"], "optgroup", ret="label")
            channels = common.parseDOM(response["content"], "optgroup")

            for i, group in enumerate(groups):
              uri = sys.argv[0] + '?mode=channel&url=%s'%urllib.quote_plus(url) + '&index=%s'%int(i)
              item = xbmcgui.ListItem(self.encode(group), iconImage = self.icon, thumbnailImage = self.icon)
              xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        else:
            self.showErrorMessage("listCategories(): bad response status%s"%response["status"])


    def listChannels(self, url, index):
        print "*** ListChannels %s"%url

        response = common.fetchPage({"link": url})

        if response["status"] == 200:
            select = common.parseDOM(response["content"], "select", attrs = { "id":"ch" })
            groups = common.parseDOM(response["content"], "optgroup")

            if groups:
              category = groups[int(index)]
            else:
              category = select

            links = common.parseDOM(category, "option", ret="value")
            titles = common.parseDOM(category, "option")


            for i, title in enumerate(titles):
                uri = sys.argv[0] + '?mode=play&url=%s'%urllib.quote_plus(links[i])
                item = xbmcgui.ListItem(self.encode(title), iconImage = self.icon, thumbnailImage = self.icon)
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        else:
            self.showErrorMessage("listChannels(): bad response status%s"%response["status"])


        xbmcplugin.endOfDirectory(self.handle, True)


    def play(self, url):
        print "Try to play url%s"%url

        try:
            response = urllib2.urlopen(url, None, 5)
            print "*** Got server response"
            print response.info()

            item = xbmcgui.ListItem(path = response.geturl())
            item.setProperty('mimetype', response.info()['Content-type'])
            xbmcplugin.setResolvedUrl(self.handle, True, item)

        except urllib2.HTTPError, e:
            print "***** Oops, HTTPError ", str(e.code)
            if e.code == 401:
                print "401 Unauthorized"
            return False
        except urllib2.URLError, e:
            print "***** Oops, URLError", str(e.args)

            # skip rtsp:// and mmsh:// protocols
            if not str(e.args).find("rtsp") == -1 or not str(e.args).find("mmsh") == -1:
                item = xbmcgui.ListItem(path = url)
                xbmcplugin.setResolvedUrl(self.handle, True, item)
            else:
                try:
                    request = urllib2.Request(url)
                    opener = urllib2.build_opener(SmartRedirectHandler())
                    auth_url = opener.open(request)

                    print "*** Try auth URL"
                    item = xbmcgui.ListItem(path = auth_url)
                    xbmcplugin.setResolvedUrl(self.handle, True, item)
                except:
                    print "*** Unable to play this URL %s"%url

        except httplib.InvalidURL, e:
            try:
                request = urllib2.Request(url)
                opener = urllib2.build_opener(SmartRedirectHandler())
                auth_url = opener.open(request)

                item = xbmcgui.ListItem(path = auth_url)
                xbmcplugin.setResolvedUrl(self.handle, True, item)

            except:
                print "*** Unable to play this URL %s"%url
        except socket.timeout, e:
            print "***** Oops timed out! ", str(e.args)
            return False
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return []

    def showErrorMessage(self, msg):
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)"%("ERROR",msg, str(10*1000)))

    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')

iptv = IPTV()
iptv.main()
