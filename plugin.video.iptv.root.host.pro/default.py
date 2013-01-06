#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.4
# -*- coding: utf-8 -*-

import xbmcplugin,xbmcgui,xbmcaddon
import os, sys, urllib, urllib2, httplib, socket
import XbmcHelpers
common = XbmcHelpers

handle = int(sys.argv[1])

__addon__ = xbmcaddon.Addon(id='plugin.video.iptv.root.host.pro')
addon_icon    = __addon__.getAddonInfo('icon')
addon_path    = __addon__.getAddonInfo('path')

CATEGORIES = [
                'Standard',
                'Sport',
                'Kinder',
                'Kino',
                'Music',
                'Ukraina',
                'Poznowatelnie',
                'Alternative'
            ]


class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)
        result.status = code
        return result

    def http_error_302(self, req, fp, code, msg, headers):
        print "Authenticate and get real stream URL"
        return headers['Location']

def listCategories():
    print "List categories"
    for i, category in enumerate(sorted(CATEGORIES)):
        url = 'http://iptv.root-host.pro/kat.php?kat='+category

        uri = sys.argv[0] + '?mode=channels&url=%s'%urllib.quote_plus(url)
        item = xbmcgui.ListItem(category, iconImage=addon_icon, thumbnailImage=addon_icon)
        xbmcplugin.addDirectoryItem(handle, uri, item, True)

    xbmcplugin.endOfDirectory(handle, True)


def listChannels(url):
    print "listChannels"
    print url

    page = common.fetchPage({"link": url})

    if page["status"] == 200:
        titles = common.parseDOM(page["content"], "title")
        links = common.parseDOM(page["content"], "stream_url")

        try:
            for i, title in enumerate(titles):
                title = title.replace('<![CDATA[', '').replace(']]>', '')
                link = links[i].replace('<![CDATA[', '').replace(']]>', '')

                uri = sys.argv[0] + '?mode=play&url=%s'%urllib.quote(link)
                item = xbmcgui.ListItem(title, iconImage=addon_icon, thumbnailImage=addon_icon)
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(handle, uri, item, False)
        except IndexError, e:
            print e

    xbmcplugin.endOfDirectory(handle, True)

def play(url):
    print "Try to play url%s"%url

    try:
        response = urllib2.urlopen(url, None, 5)
        print "*** Got server response"
        print response.info()

        item = xbmcgui.ListItem(path = response.geturl())
        item.setProperty('mimetype', response.info()['Content-type'])
        xbmcplugin.setResolvedUrl(handle, True, item)

    except urllib2.HTTPError, e:
        print "***** Oops, HTTPError ", str(e.code)
        if e.code == 401:
            print "401 Unauthorized"
        return False
    except urllib2.URLError, e:
        print "***** Oops, URLError", str(e.args)

        if not str(e.args).find("rtsp") == -1 or not str(e.args).find("mmsh") == -1:
            item = xbmcgui.ListItem(path = url)
            xbmcplugin.setResolvedUrl(handle, True, item)
        else:
            try:
                request = urllib2.Request(url)
                opener = urllib2.build_opener(SmartRedirectHandler())
                auth_url = opener.open(request)

                print "*** Try auth URL"
                item = xbmcgui.ListItem(path = auth_url)
                xbmcplugin.setResolvedUrl(handle, True, item)
            except:
                print "*** Unable to play this URL %s"%auth_url

    except httplib.InvalidURL, e:
        try:
            request = urllib2.Request(url)
            opener = urllib2.build_opener(SmartRedirectHandler())
            auth_url = opener.open(request)

            item = xbmcgui.ListItem(path = auth_url)
            xbmcplugin.setResolvedUrl(handle, True, item)

        except:
            print "*** Unable to play this URL %s"%auth_url
    except socket.timeout, e:
        print "***** Oops timed out! ", str(e.args)
        return False
    except:
        print "Unexpected error:", sys.exc_info()[0]
        return []

params = common.getParameters(sys.argv[2])
mode = params['mode'] if params.has_key('mode') else None
url = urllib.unquote_plus(params['url']) if params.has_key('url') else None

if mode == 'play':
    play(url)
elif mode == 'channels':
    listChannels(url)
elif mode == None:
    listCategories()
