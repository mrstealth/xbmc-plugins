#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.1
# -*- coding: utf-8 -*-

import os, sys, urllib, urllib2, cookielib
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import json, CommonFunctions

common = CommonFunctions

class Xmusic():
  def __init__(self):
    self.id = 'plugin.audio.xmusic.me'
    self.addon = xbmcaddon.Addon(self.id)
    self.icon = self.addon.getAddonInfo('icon')
    self.path = self.addon.getAddonInfo('path')
    self.profile = self.addon.getAddonInfo('profile')

    self.language = self.addon.getLocalizedString
    self.handle = int(sys.argv[1])
    self.url = 'http://xmusic.me'

    self.username = self.addon.getSetting('username') if self.addon.getSetting('username') else None
    self.password = self.addon.getSetting('password') if self.addon.getSetting('password') else None

    self.cookie_file = os.path.join(xbmc.translatePath(self.profile), 'cookie.txt')
    self.cookie = cookielib.LWPCookieJar()
    
    #self.token = self.getAPIkey()


  def main(self):
    params = common.getParameters(sys.argv[2])
    mode = url = style = playlist = None
    #title = artist = playlist = language = None

    mode = params['mode'] if params.has_key('mode') else None
    url = urllib.unquote_plus(params['url']) if params.has_key('url') else None
    #playlist = params['playlist'] if params.has_key('playlist') else None
    language = params['language'] if params.has_key('language') else None

    if mode == 'play':
      self.play(url)
    if mode == 'search':
      self.search()
    if mode == 'songs':
      self.getSongs(url)
    if mode == 'playlists':
      self.getPlaylists(url)
    elif mode == None:
      self.menu()


  def menu(self):
    #self.login()
    self.getMusicStyles()
#     uri = sys.argv[0] + '?mode=%s'%('search')
#     item = xbmcgui.ListItem('[COLOR=FF00FF00][%s][/COLOR]'%self.language(1000), iconImage=self.icon)
#     xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
#     
#     uri = sys.argv[0] + '?mode=%s&url=%s'%('playlists', 'http://muzebra.com/user/playlist')
#     item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s (muzebra.com)[/COLOR]"%self.language(2000), iconImage=self.icon)
#     xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
# 
#     uri = sys.argv[0] + '?mode=%s&url=%s&playlist=%s'%('songs', 'http://muzebra.com/charts/', 'Ru charts')
#     item = xbmcgui.ListItem(self.language(4001), iconImage=self.icon)
#     xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
# 
#     uri = sys.argv[0] + '?mode=%s&url=%s&playlist=%s'%('songs', 'http://muzebra.com/charts/en/', 'Ru charts')
#     item = xbmcgui.ListItem(self.language(4002), iconImage=self.icon)
#     xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

#    xbmcplugin.endOfDirectory(self.handle, True)


  def getMusicStyles(self):
    page = common.fetchPage({"link": self.url})
    styles = common.parseDOM(page["content"], "ul", attrs = { "class" : "music_styles" })
    links = common.parseDOM(styles, "a", ret="href")
    titles = common.parseDOM(styles, "a")
    
    for i, title in enumerate(titles):
      uri = sys.argv[0] + '?mode=%s&url=%s'%('songs', urllib.quote_plus(self.url+links[i]))
      item = xbmcgui.ListItem(title, iconImage=self.icon)
      xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    xbmcplugin.endOfDirectory(self.handle, True)
        
    
#   def getPlaylists(self, url):
#     print "*** GET PLAYLISTS %s"%url
#     self.login()
# 
#     headers = {
#       "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#       "Accept-Encoding": "gzip,deflate",
#       "Accept-Language" : "de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
#       "Connection" : "keep-alive",
#       "Host" : "muzebra.com",
#       "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/17.0 Firefox/17.0",
#     }
# 
#     request = urllib2.Request(url)
#     response = urllib2.urlopen(request)
# 
#     content = common.parseDOM(response.read(), "ul", attrs = { "data-id":"playlist" })
#     playlists = common.parseDOM(content, "a", attrs = { "class":"hash" })
#     pids = common.parseDOM(content, "li", ret = "data-id")
# 
#     for i, playlist in enumerate(playlists):
#       uri = sys.argv[0] + '?mode=%s&url=%s&playlist=%s'%('songs', urllib.quote_plus("http://muzebra.com/playlist/%s/"%pids[i]), playlist)
#       item = xbmcgui.ListItem(playlist, iconImage=self.icon)
#       xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
# 
#     xbmcplugin.endOfDirectory(self.handle, True)


  def getSongs(self, url):
    print "*** GET SONGS FOR PLAYLIST: %s songs"%url
 
    page = common.fetchPage({"link": url})
    playlist = common.parseDOM(page["content"], "ul", attrs = { "id" : "playlist" })

    artists = common.parseDOM(playlist, "em")
    titles = common.parseDOM(playlist, "span")
    links = common.parseDOM(playlist, "li", attrs = { "class":"track" }, ret="data-download")
    durations = common.parseDOM(playlist, "i")
        
    style = common.parseDOM(page["content"], "h2", attrs = { "class":"std" })[0]

    for i, title in enumerate(titles):
      song = "%s - %s"%(title, artists[i])

      uri = sys.argv[0] + '?mode=%s&url=%s'%('play', links[i])
      item = xbmcgui.ListItem(song, iconImage=self.icon, thumbnailImage=self.icon)

      item.setInfo(type='music',
        infoLabels = {
          'title': song,
          'artist' : artists[i],
          'album' : style,
          'genre': 'muzebra.com',
          'duration' : self.duration(durations[i].split('</a>')[-1]),
          'rating' : '5'
        }
      )

      item.setProperty('IsPlayable', 'true')
      xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

    xbmcplugin.endOfDirectory(self.handle, True)


  def getSongByID(self, sid):
    print "*** getSongByID %s"%sid
    api = "https://api.vk.com/method/audio.getById.json?&access_token=%s&audios=%s"%(self.token, sid)
    response = json.loads(common.fetchPage({"link": api})["content"])['response'][0]
    return {'url' : response['url'], 'title' : response['title'], 'artist' : response['artist']}


  def play(self, url):
    print "*** play URL %s"%url
    item = xbmcgui.ListItem(path = url)
    item.setProperty('mimetype', 'audio/mpeg')
    xbmcplugin.setResolvedUrl(self.handle, True, item)


  def duration(self, time):
    duration = time.split(':')
    return int(duration[0]) * 60 + int(duration[1])

  #  get API key for savestreaming.com and vk.com
  # hash = savestreaming.com
  # token = vk.com
  def getAPIkey(self):
    url = 'http://muzebra.com/service/user/playerparams/'
    
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
      return json.loads(response)['token']

    except:
        print "Unexpected error:", sys.exc_info()
        self.showErrorMessage("muzebra.com API error!")
        xbmcplugin.endOfDirectory(self.handle, True)
            
  def getSongFanart(self, artist):
    token = "fbd57a1baddb983d1848a939665310f6"
    url = "http://ws.audioscrobbler.com/2.0/?autocorrect=1&api_key=%s&method=artist.getImages&artist=%s"%(token, artist)
    page = common.fetchPage({"link": url})
    print page

  def search(self):
    query = common.getUserInput(self.language(1000), "")
    url = self.url + '/search/?q=' + query

    if query != None:
      self.getSongs(url, self.language(1000))
    else:
      main()
        
  # login to muzebra.com
  def login(self):
    print "*** Login"

    if self.username is None or self.password is None or self.username is '' or self.password is '':
        self.showErrorMessage(self.language(2003).encode('utf-8'))
        return False
    else:
      url = 'http://xmusic.me/authorization'

      data = urllib.urlencode({
        "action" : "authorization",
        "email" : "mrstealth2012@yandex.com",
        "password" : "reo110282",
        "post" : "yes"
      })

      headers = {
        "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language" : "en-US,en;q=0.5",
        "Connection" : "keep-alive",
        "Content-Type" : "application/x-www-form-urlencoded",
        "Host" : "xmusic.me",
        "Referer" : url,
        "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/17.0 Firefox/17.0"
      }

#DNT	1

      cj = cookielib.LWPCookieJar()

      if os.path.isfile(self.cookie_file):
        print "### Load cookie from file"
        self.cookie.load(self.cookie_file)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        urllib2.install_opener(opener)
      else:
        print "### Get cookie from server"
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        urllib2.install_opener(opener)
        request = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(request)
        print response.geturl()

    for index, cookie in enumerate(self.cookie):
      print index, '  :  ', cookie
      self.cookie.save(self.cookie_file)
    print '*************\n'


  def showErrorMessage(self, msg):
    print msg
    xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)"%("ERROR",msg, str(10*1000)))


  def encode(self, string):
    return string.decode('cp1251').encode('utf-8')


xmusic = Xmusic()
xmusic.main()
