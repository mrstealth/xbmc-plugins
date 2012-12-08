#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 2.0.5
# -*- coding: utf-8 -*-

import os, sys, urllib, urllib2, cookielib
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import json, CommonFunctions

common = CommonFunctions

class Muzebra():
  def __init__(self):
    self.id = 'plugin.audio.muzebra.com'
    self.addon = xbmcaddon.Addon(self.id)
    self.icon = self.addon.getAddonInfo('icon')
    self.path = self.addon.getAddonInfo('path')
    self.profile = self.addon.getAddonInfo('profile')

    self.language = self.addon.getLocalizedString
    self.handle = int(sys.argv[1])
    self.url = 'http://muzebra.com'

    self.username = self.addon.getSetting('username') if self.addon.getSetting('username') else None
    self.password = self.addon.getSetting('password') if self.addon.getSetting('password') else None

    # TODO: set expiry date and remove file if cookie expired
    self.cookie_file = os.path.join(xbmc.translatePath(self.profile), 'cookie.txt')
    self.cookie = cookielib.LWPCookieJar()

    self.authenticated = False

    self.token = self.getAPIkey()


  def main(self):
    params = common.getParameters(sys.argv[2])
    mode = url = playlist = None
    #title = artist = playlist = language = None

    mode = params['mode'] if params.has_key('mode') else None
    url = urllib.unquote_plus(params['url']) if params.has_key('url') else None
    playlist = params['playlist'] if params.has_key('playlist') else 'Unknown'
    artists = params['artists'] if params.has_key('artists') else 'Unknown'
    lang = params['lang'] if params.has_key('lang') else None
    page = params['page'] if params.has_key('page') else 1


    if mode == 'play':
      self.play(url)
    if mode == 'search':
      self.search()
    if mode == 'songs':
      self.getSongs(url, playlist)
    if mode == 'playlists':
      self.getPlaylists(url)
    if mode == 'artists':
      self.listArtists(url)
    if mode == 'alphabet':
        self.alphabet(url, lang)
    elif mode == None:
      self.menu()


  def menu(self):
    self.login()

    uri = sys.argv[0] + '?mode=%s'%('search')
    item = xbmcgui.ListItem('[COLOR=FF00FF00][%s][/COLOR]'%self.language(1000), iconImage=self.icon)
    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    print "*** Authenticated user? %s"%self.authenticated

    if self.authenticated:
      uri = sys.argv[0] + '?mode=%s&url=%s'%('playlists', 'http://muzebra.com/user/playlist')
      item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s (muzebra.com)[/COLOR]"%self.language(2000), iconImage=self.icon)
      xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    uri = sys.argv[0] + '?mode=%s&url=%s'%('songs', 'http://muzebra.com/charts/')
    item = xbmcgui.ListItem(self.language(4001), iconImage=self.icon)
    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    uri = sys.argv[0] + '?mode=%s&url=%s'%('songs', 'http://muzebra.com/charts/en/')
    item = xbmcgui.ListItem(self.language(4002), iconImage=self.icon)
    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    uri = sys.argv[0] + '?mode=%s&url=%s&lang=%s'%('alphabet', 'http://muzebra.com/artists/', 'ru')
    item = xbmcgui.ListItem(self.language(5001), iconImage=self.icon)
    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    uri = sys.argv[0] + '?mode=%s&url=%s&lang=%s'%('alphabet', 'http://muzebra.com/artists/', 'en')
    item = xbmcgui.ListItem(self.language(5002), iconImage=self.icon)
    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
    
    xbmcplugin.endOfDirectory(self.handle, True)


  def getPlaylists(self, url):
    print "*** GET PLAYLISTS %s"%url
    self.login()

    page = common.fetchPage({"link": url})
    content = common.parseDOM(page["content"], "ul", attrs = { "data.id":"Playlist" })
    playlists = common.parseDOM(content, "a", attrs = { "class":"hash" })
    pids = common.parseDOM(content, "li", ret = "data-id")

    for i, playlist in enumerate(playlists):
      uri = sys.argv[0] + '?mode=%s&url=%s&playlist=%s'%('songs', urllib.quote_plus("http://muzebra.com/playlist/%s/"%pids[i]), playlist)
      item = xbmcgui.ListItem(playlist, iconImage=self.icon)
      xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    xbmcplugin.endOfDirectory(self.handle, True)


  def getSongs(self, url, playlist):
    print "*** GET SONGS FOR PLAYLIST: %s songs"%url

    page = common.fetchPage({"link": url})
    content = common.parseDOM(page["content"], "div", attrs = { "id" : "content" })
    playlists = common.parseDOM(content, "ul")

    artists = common.parseDOM(playlists, "a", attrs = { "class":"hash artist" })
    titles = common.parseDOM(playlists, "span", attrs = { "class":"name" })
    sids = common.parseDOM(playlists, "a", attrs = { "class":"info" }, ret="data-aid")
    times = common.parseDOM(playlists, "div", attrs = { "class":"time" })
    
    for i, title in enumerate(titles):
      song = "%s - %s"%(title, artists[i])

      uri = sys.argv[0] + '?mode=%s&url=%s'%('play', sids[i])
      item = xbmcgui.ListItem(song, iconImage=self.icon, thumbnailImage=self.icon)

      item.setInfo(type='music',
        infoLabels = {
          'title': song,
          'album' : playlist,
          'genre': 'muzebra.com',
          'duration' : self.duration(times[i]),
          'rating' : '5'
        }
      )

      item.setProperty('IsPlayable', 'true')
      xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

    self.showMore(url, content)
    xbmcplugin.endOfDirectory(self.handle, True)


  def getSongByID(self, sid):
    api = "https://api.vk.com/method/audio.getById.json?&access_token=%s&audios=%s"%(self.token, sid)
    response = json.loads(common.fetchPage({"link": api})["content"])['response'][0]
    return {'url' : response['url'], 'title' : response['title'], 'artist' : response['artist']}


  def listArtists(self, url):
    print "*** list artists %s"%url
    
    page = common.fetchPage({"link": url})

    if page["status"] == 200:
        artists = common.parseDOM(page["content"], "ul", attrs = { "class":"artists span6" })
        links = common.parseDOM(artists, "a", attrs = { "class":"hash" }, ret="href")
        titles = common.parseDOM(artists, "a")

        for i, link in enumerate(links):
          title = titles[i].upper()
          uri = sys.argv[0] + '?mode=%s&url=%s&playlist=%s'%('songs', urllib.quote_plus(self.url+link), title)

          item = xbmcgui.ListItem(title, iconImage = self.icon, thumbnailImage = self.icon)
          xbmcplugin.addDirectoryItem(self.handle, uri, item, isFolder=True)
 
    xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.endOfDirectory(self.handle, True)
    
    
  def alphabet(self, url, lang):
    page = common.fetchPage({"link": url})
    
    print "*** get alphabet %s"%url
    
    if page["status"] == 200:
      if lang == 'ru':
        letters = common.parseDOM(page["content"], "ul", attrs = { "class":"ru" })
      else:
        letters = common.parseDOM(page["content"], "ul", attrs = { "class":"en" })
    
      links = common.parseDOM(letters, "a", attrs = { "class":"hash" }, ret="href")
      titles = common.parseDOM(letters, "a")
    
      if lang == 'ru':
        links.insert(1, '/artists/%D0%B0/')
        titles.insert(1, '\xd0\xb0')
    
      for i, link in enumerate(links):
        url = urllib.quote_plus(self.url + links[i])
        uri = sys.argv[0] + '?mode=artists'
        uri += '&url='  + url
        title = titles[i]
                
        item = xbmcgui.ListItem(title.upper(), iconImage = self.icon, thumbnailImage = self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, isFolder=True)
    
    xbmcplugin.endOfDirectory(self.handle, True)
    
  def showMore(self, url, content):
    pagination = common.parseDOM(content, "div", attrs = { "class":"pagination" })

    if pagination:
      title = common.parseDOM(content, "a", attrs = {"class": "stat"})[0]
      link = common.parseDOM(content, "a", ret="href", attrs = {"class": "stat"})[0]
      
      if url.find('page') == -1:
        url = url.replace(' ', '+') + '&page=2'
      else:
        page = int(url.split('=')[-1])
        url = url[:-1]+str(page+1)
        
      uri = sys.argv[0] + '?mode=%s&url=%s'%('songs', urllib.quote_plus(url))
      item = xbmcgui.ListItem('[COLOR=FF00FFF0]%s[/COLOR]'%title, iconImage = self.icon, thumbnailImage = self.icon)
      xbmcplugin.addDirectoryItem(self.handle, uri, item, isFolder=True)
  
  
  def play(self, sid):
    song = self.getSongByID(sid)
    item = xbmcgui.ListItem(path = song['url'], iconImage=self.icon)
    item.setInfo(type='music', infoLabels = {'title': song['title'], 'artist' : song['artist'] })
    item.setProperty('mimetype', 'audio/mpeg')
    xbmcplugin.setResolvedUrl(self.handle, True, item)


  def duration(self, time):
    duration = time.split(':')
    return int(duration[0]) * 60 + int(duration[1])


  #  get API key for savestreaming.com
  def getAPIkey(self):
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
      return json.loads(response)['token']
    except  urllib2.URLError, e:
      if hasattr(e, 'reason'):
        self.showErrorMessage('We failed to reach a muzebra.com server %s'%e.reason)
      elif hasattr(e, 'code'):
        print 'The server couldn\'t fulfill the request.'
        self.showErrorMessage('The server couldn\'t fulfill the request. %s'%e.code)


  def search(self):
    query = common.getUserInput(self.language(1000), "")
    url = self.url + '/search/?q=' + query

    if query != None:
      self.getSongs(url, self.language(1000))
    else:
      main()
      

  # login to muzebra.com
  def login(self):
    print "*** Login to muzebra.com"

    if self.username is None or self.password is None or self.username is '' or self.password is '':
        self.authenticated = False
        return False
    else:
      url = 'http://muzebra.com/user/login'
      #url = 'http://muzebra.com/service/forms/login'

      data = urllib.urlencode({
        "UserLogin[username]" : self.username,
        "UserLogin[password]" : self.password,
        "UserLogin[rememberMe]" : "1"
      })

      headers = {
        "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language" : "de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
        "Connection" : "keep-alive",
        "Content-Type" : "application/x-www-form-urlencoded",
        "Host" : "muzebra.com",
        "Referer" : self.url,
        "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/17.0 Firefox/17.0"
      }

      cj = cookielib.LWPCookieJar()

      if os.path.isfile(self.cookie_file):
        print "### Load cookie from file"
        self.cookie.load(self.cookie_file)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        urllib2.install_opener(opener)

        self.authenticated = True
        return True
      else:
        print "### Get cookie from server"
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        urllib2.install_opener(opener)
        request = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(request)

        if response.geturl() == "http://muzebra.com/user/profile":
          self.authenticated = True
          for index, cookie in enumerate(cj):
            print index, '  :  ', cookie
            cj.save(self.cookie_file)

          return True
        else:
          print response.geturl()
          return False


  def showErrorMessage(self, msg):
    print msg
    xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)"%("ERROR",msg, str(10*1000)))


  def encode(self, string):
    return string.decode('cp1251').encode('utf-8')


muzebra = Muzebra()
muzebra.main()
