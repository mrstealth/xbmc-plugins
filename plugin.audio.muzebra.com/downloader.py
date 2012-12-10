#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.0
# -*- coding: utf-8 -*-

import xbmcgui, xbmcaddon, xbmcvfs
import urllib, urllib2, re, os, sys, socket, cookielib, errno
import simplejson as json

Addon = xbmcaddon.Addon(id='plugin.audio.muzebra.com')
addon_icon = Addon.getAddonInfo('icon')
addon_path = Addon.getAddonInfo('path')
language = Addon.getLocalizedString


# def getAPIkey():
#  url = 'http://muzebra.com/service/user/playerparams/'
#  http_header = {
#                "Accept" : "application/json, text/javascript, */*; q=0.01",
#                "Accept-Language" : "de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
#                "Accept-Charset" : "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
#                "DNT" : "1",
#                "Host" : "muzebra.com",
#                "Origin" : "http://muzebra.com",
#                "Referer" : "http://muzebra.com/",
#                "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0",
#                "X-Requested-With" : "XMLHttpRequest"
#  }
#
#  params = {}
#
#  # setup socket connection timeout
#  timeout = 15
#  socket.setdefaulttimeout(timeout)
#
#  # setup cookie handler
#  cookie_jar = cookielib.LWPCookieJar()
#  cookie = urllib2.HTTPCookieProcessor(cookie_jar)
#
#  # setup proxy handler, in case some-day you need to use a proxy server
#  proxy = {} # example: {"http" : "www.blah.com:8080"}
#
#  # create an urllib2 opener()
#  #opener = urllib2.build_opener(proxy, cookie) # with proxy
#  opener = urllib2.build_opener(cookie) # we are not going to use proxy now
#
#  # create your HTTP request
#  req = urllib2.Request(url, urllib.urlencode(params), http_header)
#
#  # submit your request
#  res = opener.open(req)
#  html = res.read()
#  return json.loads(html)['hash'] + '/'

#  get API key for savestreaming.com
def getAPIkey():
  url = 'http://muzebra.com/service/playerparams/'

  headers = {
   "Accept" : "application/json, text/javascript, */*; q=0.01",
   "Accept-Language" : "de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
   "Accept-Charset" : "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
   "DNT" : "1",
   "Host" : "muzebra.com",
   "Origin" : "http://muzebra.com",
   "Referer" : "http://muzebra.com/",
   "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0",
   "X-Requested-With" : "XMLHttpRequest"
  }

  try:
    request = urllib2.Request(url, urllib.urlencode({}), headers)
    response = urllib2.urlopen(request).read()
    return json.loads(response)['hash'] + '/'
  except  urllib2.URLError, e:
    if hasattr(e, 'reason'):
      self.showErrorMessage('We failed to reach a muzebra.com server %s'%e.reason)
    elif hasattr(e, 'code'):
      print 'The server couldn\'t fulfill the request.'
      self.showErrorMessage('The server couldn\'t fulfill the request. %s'%e.code)

def getFileName(url):
    response = urllib2.urlopen(url, None, 1)
    disposition =  response.info()['Content-Disposition']
    return re.search('"(.*?)"', disposition).group(0)


def construct_mp3_url(aid):
    key  = getAPIkey()
    if len(aid) > 0:
        url = 'http://savestreaming.com/t/%s'%aid + '_%s'%key
        return url
    else:
        return ''

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def getDownloadFolder():
    folder = Addon.getSetting('folder')
    return False if folder == 'None' else folder

def download(aid, title, path):
    url = construct_mp3_url(aid)

    if url:
      #title = getFileName(url).replace('\"', "")
      title = title + '.mp3'
      source = url
      destination = path + title

      try:
          dialog = xbmcgui.DialogProgress()
          dialog.create("MP3 Downloader","Please wait, downloading file ...")
          xbmcvfs.copy(source, destination)

      except:
          print "Uncatch exception"
      else:
          dialog.close()
    else:
        print "Show notification: Can't get MP3 url"


# ***** MAIN *****
args = sys.argv[1]
args = sys.argv[1].split("|")

print args

if sys.argv[1]:
  folder = getDownloadFolder()
  if folder:
    download(args[0], args[1], folder)
  else:
    dialog = xbmcgui.Dialog()
    path = dialog.browse(0, 'Choose download directory', 'music', '', False, False)

    if path:
      download(args[0], args[1], path)
    else:
      print "Please select a path"
else:
  print "Error: show XBMC notification"
