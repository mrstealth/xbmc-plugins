#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.0
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys
import HTMLParser, CommonFunctions
import xbmcaddon, xbmcgui, xbmcplugin
import simplejson as json

Addon = xbmcaddon.Addon(id='plugin.audio.muzebra.com')
addon_icon  = Addon.getAddonInfo('icon')
addon_path  = Addon.getAddonInfo('path')
language = Addon.getLocalizedString

handle = int(sys.argv[1])
common = CommonFunctions

def construct_url(mode, url=False, title=False, artist=False, category=False):
    uri = sys.argv[0] + '?mode=' + mode
    if url: uri += '&url=' + urllib.quote_plus(url)
    if artist: uri += '&artist=' + artist
    if category: uri += '&category=' + category
    return uri

def construct_mp3_url(aid):
    if len(aid) > 0:
        url = 'http://savestreaming.com/t/%s'%aid + '_a625de3a4e/'
        return url
    else:
        return ''

def xbmcItem(mode, url, title, icon=False, action=False):
    uri = sys.argv[0] + '?mode='+ mode
    uri += '&url=' + url
    uri += '&title=' + title

    if not icon: icon = addon_icon
    item = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon)
    item.setProperty('IsPlayable', 'false')

    if not action:
      xbmcplugin.addDirectoryItem(handle, uri, item, True)
    else:
      # FIXME: add label to params
      print "Add context menu to item"

def xbmcContextMenuItem(item, title, identifier):
    script = addon_path + '/downloader.py'
    params = "%s"%construct_mp3_url(identifier)
    runner = "XBMC.RunScript(" + str(script)+ ", " + params + ")"
    item.addContextMenuItems([(language(6000), runner)])

def check_url(url):
    try:
        response = urllib2.urlopen(url, None, 1)
        #print "\n*** Info for: " + url
        #print response.geturl()
        #print response.info()

    except urllib2.HTTPError, e:
        #print "***** Oops, HTTPError ", str(e.code)
        return False
    except urllib2.URLError, e:
        #print "***** Oops, URLError", str(e.args)
        return False
    except socket.timeout, e:
        #print "***** Oops timed out! ", str(e.args)
        return False
    except:
        #print "Unexpected error:", sys.exc_info()[0]
        return False
    else:
        return True

# *** Python helpers ***
def strip_html(text):
	def fixup(m):
		text = m.group(0)
		if text[:1] == "<":
			if text[1:3] == 'br':
				return '\n'
			else:
				return ""
		if text[:2] == "&#":
			try:
				if text[:3] == "&#x":
					return chr(int(text[3:-1], 16))
				else:
					return chr(int(text[2:-1]))
			except ValueError:
				pass
		elif text[:1] == "&":
			import htmlentitydefs
			if text[1:-1] == "mdash":
				entity = " - "
			elif text[1:-1] == "ndash":
				entity = "-"
			elif text[1:-1] == "hellip":
				entity = "-"
			else:
				entity = htmlentitydefs.entitydefs.get(text[1:-1])
			if entity:
				if entity[:2] == "&#":
					try:
						return chr(int(entity[2:-1]))
					except ValueError:
						pass
				else:
					return entity
		return text
	ret =  re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)
	return re.sub("\n+", '\n' , ret)

def remove_extra_spaces(data):  # Remove more than one consecutive white space
    p = re.compile(r'\s+')
    return p.sub(' ', data)

def unescape(entity, encoding):
  if encoding == 'utf-8':
    return HTMLParser.HTMLParser().unescape(entity).encode(encoding)
  elif encoding == 'cp1251':
    return entity.decode(encoding).encode('utf-8')

def uniq(alist):    # Fastest order preserving
    set = {}
    return [set.setdefault(e,e) for e in alist if e not in set]

def duration_in_sec(duration):
  time = duration.split(':')
  return int(time[0]) * 60 + int(time[1])
